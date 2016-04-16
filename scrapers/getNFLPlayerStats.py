#date created 10/25/15
import sys
import re
import json
from collections import defaultdict
from robobrowser import RoboBrowser
from pymongo import MongoClient
from datetime import datetime
from multiprocessing import Pool


from robobrowserWrapper import open_or_follow_link, get_proxy_count, get_user_agent
sys.path.append('../')
from logWrapper import makeLogger, closeLogger
from utilities import convertToNumber, cleanKey

client = MongoClient('localhost', 27017)
db = client['fantasy']
col_player_profiles = db['player_profiles']
col_player_career_stats = db['player_career_stats']
col_player_game_logs = db['player_game_logs']
col_player_splits = db['player_splits']
col_player_drafts = db['player_drafts']
col_player_combines = db['player_combines']


#connect each player colection to nfl_team_stats, fanduel_prices, nfl_schedule
#offensive lineman are missing

def getPlayerTabUrl(playerUrl, tabName):
    return ''.join(playerUrl.rsplit('/', 1)[:-1]) + '/' + tabName

def parsePlayerBio(logger, playerBio, playerUrl):

    startTime = datetime.now()

    logger.debug('Starting playerBio')

    playerBioDict = {'player_url': playerUrl}
    for lineNumber, line in enumerate(playerBio.find_all('p')):
        try:
            if lineNumber == 0:
                firstName, lastName = line.find(class_="player-name").text.strip().split(' ')
                playerBioDict['firstName'] = firstName
                playerBioDict['lastName'] = lastName
                playerNumber, position = line.find(class_="player-number").text.strip().split(' ')
                playerBioDict['playerNumber'] = playerNumber[1:]
                playerBioDict['position'] = position

            elif lineNumber == 1:
                continue
            else:
                playerBioDict.update({keyValue[0].strip(): keyValue[1].strip() for keyValue in re.findall('(.*): ?(.*)', line.text)})
        except:
            logger.exception('failed parsing playerBio %s', playerUrl)
            return False
    
    try:
        logger.debug('Checking if player profile exists again')
        if col_player_profiles.find({'player_url': playerUrl}).count():
            logger.debug('player profile exists')
            return False
        logger.debug('Creating playerBioDict')
        return col_player_profiles.insert(playerBioDict)
    except:
        logger.exception('insert_many error')

    print False

def parseCareerStats(logger, careerStats, player_profile_id):
    """
    Parses career stats page for given player
    Stores each row in its own doc
    """
    startTime = datetime.now()

    logger.debug('Starting careerStats')

    careerStats_list = []
    for tableNumber, careerStat in enumerate(careerStats):
        logger.debug('Table %d of %d', tableNumber, len(careerStats))
        try:
            tableName = careerStat.find("div").text.strip()

            tableKey = careerStat.find_all(class_="player-table-key")[-1]
            tableKey = tableKey.find_all('td')
            
            tableItems = careerStat.find("tbody").find_all("td")

            rowDict = {'tableName': tableName, 'player_profile_id': player_profile_id}
            rowYear = None
            tableColumn = 0
        except:
            logger.exception('failed parsing table')
            continue

        for index, item in enumerate(tableItems, start=1):
            logger.debug('Row %d of %d', index/len(tableKey), len(tableItems))
            try:
                if 'class' in item.attrs:
                    if item.attrs['class'][0] == 'border-td':
                        continue
                    if item.attrs['class'][0] == 'player-totals':
                        break
                if tableColumn == 0:
                    rowDict['rowYear'] = convertToNumber(item.text.strip())
                    tableColumn += 1
                    continue

                rowDict[cleanKey(tableKey[tableColumn].text)] = convertToNumber(item.text.strip())

                tableColumn += 1
                if tableColumn >= len(tableKey):
                    careerStats_list.append(rowDict)
                    rowDict = {'tableName': tableName, 'player_profile_id': player_profile_id}
                    tableColumn = 0
            except:
                logger.exception('failed parsing row %d of %s', index/len(tableKey), tableName)

    try:
        logger.debug('Bulk Creating careerStats_list')
        col_player_career_stats.insert_many(careerStats_list)
    except:
        logger.exception('insert_many error')

    logger.debug('parseCareerStats time elapsed: ' + str(datetime.now() - startTime))

def parseGameLogs(logger, gameLogs, year, player_profile_id):
    """
    Parses 1 year of games logs for given player.
    Stores each row in its own doc
    """
    startTime = datetime.now()

    logger.debug('Starting gameLogs')

    gameLogs_list = []
    #messy because of bye weeks, 1 less column present
    for tableNumber, gameLog in enumerate(gameLogs):
        logger.debug('Table %d of %d', tableNumber, len(gameLogs))
        try:
            topTableColumns = gameLog.find(class_="player-table-header").find_all('td')
            topTableKey = []
            if len(topTableColumns) > 1:
                for index, topTableColumn in enumerate(topTableColumns):
                    for _ in range(int(topTableColumn['colspan'])):
                        if index == 0:
                            topTableKey.append('')
                        else:
                            topTableKey.append(topTableColumn.text)
            tableName = topTableColumns[0].text.strip()

            tableKey = gameLog.find(class_="player-table-key")
            tableKey = tableKey.find_all('td')

            if topTableKey:
                for index, key in enumerate(tableKey):
                    if topTableKey[index]:
                        tableKey[index] = cleanKey(topTableKey[index] + '_' + key.text)
                    else:
                        tableKey[index] = cleanKey(key.text)

            tableItems = gameLog.find("tbody").find_all("td")

            rowDict = {'tableName': tableName, 'player_profile_id': player_profile_id, 'year': convertToNumber(year)}
            tableColumn = 0
            byeWeek = False
            columnsSkip = 0
            rowWeek = None
        except:
            logger.exception('failed parsing table')
            continue

        for index, item in enumerate(tableItems):
            logger.debug('Row %d of %d', index/len(tableKey), len(tableItems))
            try:
                if byeWeek:
                    if columnsSkip >= len(tableKey)-3:
                        byeWeek = False
                        columnsSkip = 0
                        tableColumn = 0
                    else:
                        columnsSkip += 1
                    continue

                #skip borders
                if 'class' in item.attrs:
                    if item.attrs['class'][0] == 'border-td':
                        continue
                #detect Total row and break
                if 'colspan' in item.attrs:
                    if item.attrs['colspan'] == "3":
                        if 'class' in tableItems[index+1].attrs:
                            if tableItems[index+1].attrs["class"][0] == "player-totals":
                                break

                if tableColumn == 0:
                    rowDict['week'] = convertToNumber(item.text.strip())
                    tableColumn += 1
                    continue

                if tableColumn == 1:
                    if item.text.strip() == "Bye":
                        byeWeek = True
                        gameDate = "Bye"
                        tableColumn +=1
                        while(tableColumn < len(tableKey)):
                            rowDict[tableKey[tableColumn]] = None
                            tableColumn += 1
                        #store nones

                if not byeWeek:
                    if tableColumn == 2:
                        opp = None
                        linksFound = len(item.find_all('a'))
                        if linksFound == 2:
                            opp = item.find_all('a')[1].text.strip()
                        elif linksFound == 1:
                            opp = item.find_all('a')[0].text.strip()
                        else:
                            opp = item.text.strip()
                        rowDict[tableKey[tableColumn]] = opp.replace('\t', '').replace('\n', '')
                        tableColumn += 1
                        continue

                    if tableColumn == 3:
                        outCome = item.find("span").text.strip()
                        score = None
                        linksFound = len(item.find_all("a"))
                        if linksFound == 1:
                            score = item.find("a").text.strip()
                        elif linksFound == 0:
                            score = re.findall('[0-9]+-[0-9]+', item.text)[0]
                        result = outCome + score
                        rowDict[tableKey[tableColumn]] = result
                        tableColumn += 1
                        continue

                    rowDict[tableKey[tableColumn]] = convertToNumber(item.text.strip())


                    tableColumn += 1
                    if tableColumn >= len(tableKey):
                        gameLogs_list.append(rowDict)
                        rowDict = {'tableName': tableName, 'player_profile_id': player_profile_id, 'year': convertToNumber(year)}
                        tableColumn = 0
                        byeWeek = False
            except:
                logger.exception('failed parsing row %d of %s', index/len(tableKey), tableName)

    try:
        logger.debug('Bulk Creating gameLogs_list')
        col_player_game_logs.insert_many(gameLogs_list)
    except:
        logger.exception('insert_many error')

    logger.debug('parseGameLogs time elapsed: ' + str(datetime.now() - startTime))

def parseSplits(logger, splits, year, splitType, player_profile_id):
    """
    """
    startTime = datetime.now()

    logger.debug('Starting %s', splitType)
    
    try:
        tabs = splits.find(class_="player-tabs")
        tabs = tabs.find_all('li')
    except:
        logger.exception('failed parsing player tabs')
        return

    splits_list = []
    for index, tab in enumerate(tabs):
        logger.debug('tab %d of %d', index, len(tabs))
        try:
            currentTabText = tab.text.strip()
            currentTab = splits.find(id='game_split_tabs_' + str(index))
            tables = currentTab.find_all('table')
        except:
            logger.exception('failed parsing player tables for tab %d of %d', index, len(tabs))
            continue

        for tableIndex, table in enumerate(tables):
            logger.debug('table %d of %d', tableIndex, len(tables))
            try:
                tableKey = table.find(class_="player-table-key")
                tableKey = tableKey.find_all('td')
                tableName = tableKey[0].text.strip()

                tableItems = table.find('tbody').find_all('td')
                rowDict = {'currentTabText': currentTabText, 'tableName': tableName, 'player_profile_id': player_profile_id, 'year': convertToNumber(year), 'splitType': splitType}
                tableColumn = 0
            except:
                logger.exception('failed parsing player table %d of %d', tableIndex, len(tables))
                continue

            for rowIndex, item in enumerate(tableItems):
                logger.debug('Row %d of %d', rowIndex/len(tableKey), len(tableItems))
                try:
                    if 'class' in item.attrs:
                        if item.attrs['class'][0] == 'border-td':
                            continue

                    if tableColumn == 0:
                        rowName = item.text.strip()
                        rowDict['rowName'] = rowName
                        tableColumn += 1
                        continue

                    rowDict[cleanKey(tableKey[tableColumn].text)] = item.text.strip()

                    tableColumn += 1
                    if tableColumn >= len(tableKey):
                        splits_list.append(rowDict)
                        tableColumn = 0
                        rowDict = {'currentTabText': currentTabText, 'tableName': tableName, 'player_profile_id': player_profile_id, 'year': convertToNumber(year), 'splitType': splitType}
                except:
                    logger.exception('failed parsing row %d of %s', rowIndex/len(tableKey), tableName)

    try:
        logger.debug('Bulk Creating splits_list')
        col_player_splits.insert_many(splits_list)
    except:
        logger.exception('insert_many error')

    logger.debug('parseSplits time elapsed: ' + str(datetime.now() - startTime))

def parseDraft(logger, draft, player_profile_id):
    
    startTime = datetime.now()

    logger.debug('Starting parseDraft')

    draftStatDict = {'player_profile_id': player_profile_id}
    try:
        draftStatDict['draftYear'] = draft.find(class_='draft-header').text.split(' ')[1]
        draftStatDict['pickNumber'] = draft.find(class_='pick-number').text
        draftStatDict['team'] = draft.find(class_='team').text
        draftStatDict['round'] = draft.find(class_='round').text
        draftStatDict['draftAnalysis'] = draft.find(class_='draft-analysis').find('p').text.encode('utf-8')
    except:
        logger.exception('failed parsing draft')
        return

    try:
        logger.debug('Inserting draftStatDict')
        return col_player_drafts.insert(draftStatDict)
    except:
        logger.exception('insert error')

    logger.debug('parseDraft time elapsed: ' + str(datetime.now() - startTime))


def parseCombine(logger, combine, player_profile_id):
    startTime = datetime.now()

    logger.debug('Starting parseCombine')

    combineStatDict = {'player_profile_id': player_profile_id}
    try:
        combineStatDict['combineYear'] = combine.find(class_='combine-header').text.split(' ')[1]
        combineStats = combine.find(id='combine-stats')
        for title in combineStats.find_all(class_='tp-title'):
            value = title.find(class_='tp-results').text
            key = title.text.replace(value, '')
            combineStatDict[key] = value
    except:
        logger.exception('failed parsing combine')
        return

    try:
        logger.debug('Inserting combineStatDict')
        return col_player_combines.insert(combineStatDict)
    except:
        logger.exception('insert error')

    logger.debug('parseCombine time elapsed: ' + str(datetime.now() - startTime))


def main():

    startTime = datetime.now()
    print startTime

    logger = makeLogger('main', r'./logs_nflPlayerStats/')

    playerUrl_set = set()

    #html5lib parser required for broken html on gameSplits
    browser = RoboBrowser(history=False, parser='html5lib')

    browser.open('http://www.nfl.com/stats/categorystats?tabSeq=0&statisticCategory=PASSING&qualified=true&season=2015&seasonType=PRE')

    statisticCategory = browser.find(id="statistic-category")
    statisticCategories = statisticCategory.find_all("option")
    season = browser.find(id="season-dropdown")
    seasons = season.find_all("option")
    seasonType = browser.find(id="season-type")
    seasonTypes = seasonType.find_all("option")

    for statisticCategory in statisticCategories:
        if statisticCategory.text == 'Category...':
            continue
        for season in seasons:
            if season.text == 'Season...':
                continue
            for seasonType in seasonTypes:
                if seasonType.text == 'Season Type...':
                    continue

                loadNextPage = True
                pageNumber = 1
                while(loadNextPage):

                    browser.open('http://www.nfl.com/stats/categorystats?tabSeq=0&statisticCategory=' + statisticCategory['value'] + '&qualified=true&season=' + season['value'] + '&seasonType=' + seasonType['value'] + '&d-447263-p=' + str(pageNumber))
                    pageNumber += 1
                    linkNavigation = browser.find(class_='linkNavigation')
                    if not linkNavigation or pageNumber > len(linkNavigation.find_all('a')):
                        loadNextPage = False

                    result = browser.find(id="result")

                    tries = 0
                    # sometimes when using slow proxies nfl.com returns 200 without the whole page being loaded
                    while not result:
                        if tries > 10:
                            raise Exception('No teams found %s' % url)
                        elif tries > 0:
                            time.sleep(random.uniform(5, 7))
                        tries += 1
                        logger.debug('No result-tries: %d', tries)
                        browser = RoboBrowser(history=False,  parser='html5lib', user_agent=get_user_agent(logger), timeout=10)
                        browser = open_or_follow_link(logger, browser, 'open', url)
                        result = browser.find(id="result")

                    tbodies = result.find_all("tbody")
                    if len(tbodies) != 2:
                        raise Exception("error parsing result")
                    tableKey = tbodies[0]
                    tableKey = tableKey.find_all("th")

                    tableItems = tbodies[1]
                    tableItems = tableItems.find_all("td")

                    tableColumn = 0
                    teamStatDict = {}
                    for tableIndex, tableItem in enumerate(tableItems):
                        if tableColumn == 0:
                            #logger.debug('Row %d of %d', tableIndex, len(tableItems))
                            tableColumn += 1
                            continue

                        if tableColumn == 1:
                            playerUrl_set.add('http://www.nfl.com' + tableItem.find('a')['href'])
                            raw_input('-->')

                        tableColumn += 1
                        if tableColumn >= len(tableKey):
                            tableColumn = 0

    for playerUrl in playerUrl_set:
        browser.open(playerUrl)
                                
        #parsePlayer BIO
        playerBio = browser.find(class_="player-info")
        player_profile_id = parsePlayerBio(logger, playerBio, playerUrl)
        raw_input('playerBio-->')

        playerUrl = browser.url
        tabNames = [tabName['href'] for tabName in browser.find(id="player-profile-tabs").find_all('a')]
        for tabName in tabNames:
            playerUrl = getPlayerTabUrl(playerUrl, tabName)

            if tabName == 'profile':
                continue

            print playerUrl
            browser.open(playerUrl)

            if tabName == 'careerstats':
                careerStats = browser.find(id="player-stats-wrapper")
                careerStats = careerStats.find_all("table")
                parseCareerStats(logger, careerStats, player_profile_id)

                raw_input('careerStats-->')
            elif tabName == 'gamelogs':
                #parse gameLogs
                gameLogYears = browser.find(id="criteria")
                gameLogYears = gameLogYears.find_all("option")
                gameLogYearList = []
                for gameLogYear in gameLogYears:
                    gameLogYearList.append(gameLogYear.text.strip())

                for gameLogYear in gameLogYearList:
                    season = browser.get_form(id="criteria")
                    season['season'].value = gameLogYear
                    browser.submit_form(season)
                    gameLogs = browser.find(id="player-stats-wrapper")
                    gameLogs = gameLogs.find_all("table")
                    parseGameLogs(logger, gameLogs, gameLogYear, player_profile_id)
                    
                raw_input('gameLogs-->')
            elif tabName == 'gamesplits':
                #parse game splits
                years = browser.find(id="criteria")
                years = years.find_all("option")
                yearsList = []
                for year in years:
                    yearsList.append(year.text.strip())
                
                

                for year in yearsList:
                    season = browser.get_form(id="criteria")
                    season['season'].value = year
                    browser.submit_form(season)

                    gameSplits = browser.find(id="player-stats-wrapper")

                    parseGameSplits(logger, gameSplits, year, 'game', player_profile_id)
                
                raw_input('splits-->')
            elif tabName == 'situationalstats':
                #parse situational stats
                years = browser.find(id="criteria")
                years = years.find_all("option")
                yearsList = []
                for year in years:
                    yearsList.append(year.text.strip())
                
                

                for year in yearsList:
                    season = browser.get_form(id="criteria")
                    season['season'].value = year
                    browser.submit_form(season)

                    situationalStats = browser.find(id="player-stats-wrapper")

                    parseGameSplits(logger, situationalStats, year, 'situational', player_profile_id)

                raw_input('situational-->')
            elif tabName == 'draft':
                draft = browser.find(id="player-stats-wrapper")
                parseDraft(logger, draft, player_profile_id)
            if tabName == 'combine':
                combine = browser.find(id="player-stats-wrapper")
                parseCombine(logger, combine, player_profile_id)

    print datetime.now()-startTime 

if __name__ == '__main__':
    main()