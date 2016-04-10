#date created 10/25/15
import re
import csv
import json
from collections import defaultdict
from robobrowser import RoboBrowser
from datetime import datetime, timedelta

#connect each player colection to nfl_team_stats, fanduel_prices, nfl_schedule

def getPlayerTabUrl(playerUrl, tabName):
    return ''.join(playerUrl.rsplit('/', 1)[:-1]) + '/' + tabName

def parsePlayerBio(playerBio):
    playerBioDict = {}
    for lineNumber, line in enumerate(playerBio.find_all('p')):
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

    print playerBioDict

def parseCareerStats(careerStats):
    print len(careerStats)

    careerStatsDict = {} # {category: {year: {stats}, ...}, ...}
    for careerStat in careerStats:
        tableName = careerStat.find("div").text.strip()
        if tableName == 'Defensive':
            continue
        tableKey = careerStat.find(class_="player-table-key")
        tableKey = tableKey.find_all('td')
        
        tableItems = careerStat.find("tbody").find_all("td")

        tableDict = defaultdict(dict)
        rowYear = None
        tableColumn = 0
        for index, item in enumerate(tableItems, start=1):
            if 'class' in item.attrs:
                if item.attrs['class'][0] == 'border-td':
                    continue
                if item.attrs['class'][0] == 'player-totals':
                    break
            if tableColumn == 0:
                rowYear = item.text.strip()
                tableColumn += 1
                continue

            tableDict[rowYear][tableKey[tableColumn].text.strip()] = item.text.strip()

            tableColumn += 1
            if tableColumn >= len(tableKey):
                tableColumn = 0
        careerStatsDict[tableName] = tableDict

    with open(r'careerStats.txt', 'w') as oF:
        oF.write(json.dumps(careerStatsDict))

    for category, stats in careerStatsDict.iteritems():
        print category
        print stats

def parseGameLogs(gameLogs):
    print len(gameLogs)

    gameLogsDict = {} # {category: {week: {stats}, ...}, ...}
    #messy because of bye weeks, 1 less column present
    for gameLog in gameLogs:
        tableName = gameLog.find(class_="player-table-header").find('td').text.strip()
        print tableName

        tableKey = gameLog.find(class_="player-table-key")
        tableKey = tableKey.find_all('td')
        print tableKey

        tableItems = gameLog.find("tbody").find_all("td")

        tableDict = defaultdict(dict)
        tableColumn = 0
        byeWeek = False
        columnsSkip = 0
        rowWeek = None
        for index, item in enumerate(tableItems):
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
                rowWeek = item.text.strip()
                tableColumn += 1
                continue

            if tableColumn == 1:
                if item.text.strip() == "Bye":
                    byeWeek = True
                    gameDate = "Bye"
                    tableColumn +=1
                    while(tableColumn < len(tableKey)):
                        tableDict[rowWeek][tableKey[tableColumn].text.strip()] = None
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
                    tableDict[rowWeek][tableKey[tableColumn].text.strip()] = opp.replace('\t', '').replace('\n', '')
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
                    tableDict[rowWeek][tableKey[tableColumn].text.strip()] = result
                    tableColumn += 1
                    continue

                tableDict[rowWeek][tableKey[tableColumn].text.strip()] = item.text.strip()


                tableColumn += 1
                if tableColumn >= len(tableKey):
                    tableColumn = 0
                    byeWeek = False
        gameLogsDict[tableName] = tableDict

    with open(r'gameLogs.txt', 'w') as oF:
        oF.write(json.dumps(gameLogsDict))

    for category, stats in gameLogsDict.iteritems():
        print category
        print stats

def parseGameSplits(gameSplits):
    tabs = gameSplits.find(class_="player-tabs")
    tabs = tabs.find_all('li')

    gameSplitDict = {} #{tabKey: tableDict}
    for index, tab in enumerate(tabs):
        currentTabText = tab.text.strip()
        currentTab = gameSplits.find(id='game_split_tabs_' + str(index))
        tables = currentTab.find_all('table')

        tableDict = {} #{tableName: rowDict}
        for table in tables:
            tableKey = table.find(class_="player-table-key")
            tableKey = tableKey.find_all('td')

            tableItems = table.find('tbody').find_all('td')
            rowDict = defaultdict(dict)
            rowKey = None
            tableColumn = 0
            for item in tableItems:
                if 'class' in item.attrs:
                    if item.attrs['class'][0] == 'border-td':
                        continue

                if tableColumn == 0:
                    rowKey = item.text.strip()
                    tableColumn += 1
                    continue

                rowDict[rowKey][tableKey[tableColumn].text.strip()] = item.text.strip()

                tableColumn += 1
                if tableColumn >= len(tableKey):
                    tableColumn = 0
            tableDict[tableKey[0].text.strip()] = rowDict
        gameSplitDict[currentTabText] = tableDict

    with open(r'3_4.txt', 'w') as oF:
        oF.write(json.dumps(gameSplitDict))
    
    for tabName, tabValues in gameSplitDict.iteritems():
        print tabName
        for tableName, table in tabValues.iteritems():
            print tableName
            for rowKey, tableValues in table.iteritems():
                print rowKey
                for tableKey, tableValue in tableValues.iteritems():
                    print tableKey, tableValue

def parseDraft(draft):
    draftStatDict = {}
    draftStatDict['draftYear'] = draft.find(class_='draft-header').text.split(' ')[1]
    draftStatDict['pickNumber'] = draft.find(class_='pick-number').text
    draftStatDict['team'] = draft.find(class_='team').text
    draftStatDict['round'] = draft.find(class_='round').text
    draftStatDict['draftAnalysis'] = draft.find(class_='draft-analysis').find('p').text.encode('utf-8')

    print draftStatDict


def parseCombine(combine):
    combineStatDict = {}
    combineStatDict['combineYear'] = combine.find(class_='combine-header').text.split(' ')[1]
    combineStats = combine.find(id='combine-stats')
    for title in combineStats.find_all(class_='tp-title'):
        value = title.find(class_='tp-results').text
        key = title.text.replace(value, '')
        combineStatDict[key] = value
    print combineStatDict


def main():

    startTime = datetime.now()
    print startTime

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
                            playerUrl = 'http://www.nfl.com' + tableItem.find('a')['href']
                            browser.open(playerUrl)
                            
                            #parsePlayer BIO
                            playerBio = browser.find(class_="player-info")
                            parsePlayerBio(playerBio)
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
                                    parseCareerStats(careerStats)

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
                                        parseGameLogs(gameLogs)
                                        
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

                                        parseGameSplits(gameSplits)
                                    
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

                                        parseGameSplits(situationalStats)

                                    raw_input('situational-->')
                                elif tabName == 'draft':
                                    draft = browser.find(id="player-stats-wrapper")
                                    parseDraft(draft)
                                if tabName == 'combine':
                                    combine = browser.find(id="player-stats-wrapper")
                                    parseCombine(combine)

                                
                            raw_input('-->')

                        tableColumn += 1
                        if tableColumn >= len(tableKey):
                            tableColumn = 0

    print datetime.now()-startTime 

if __name__ == '__main__':
    main()