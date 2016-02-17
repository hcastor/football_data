#date created 10/25/15
import re
import csv
import json
from collections import defaultdict
from robobrowser import RoboBrowser
from datetime import datetime, timedelta

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
        if tableName == 'Preseason':
            continue
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

def main():

    startTime = datetime.now()
    print startTime

    #html5lib parser required for broken html on gameSplits
    browser = RoboBrowser(history=False, parser='html5lib')

    browser.open("http://search.nfl.com/search?query=tom+brady")

    spotLight = browser.find(class_="ez-spotlights")

    #collect links
    careerStats = spotLight.select(".stats")
    gameLogs = spotLight.select(".logs")
    gameSplits = spotLight.select(".splits")
    sitStats = spotLight.select(".sitstats")
    
    #parse careerStats
    browser.follow_link(careerStats[0])
    careerStats = browser.find(id="player-stats-wrapper")
    careerStats = careerStats.find_all("table")
    parseCareerStats(careerStats)

    raw_input('careerStats-->')

    #parse gameLogs
    browser.follow_link(gameLogs[0])
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

    #parse game splits
    browser.follow_link(gameSplits[0])
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

    #parse situational stats
    browser.follow_link(sitStats[0])
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

    # gameSplits = gameSplits.find_all("table")
    # print gameSplits

    #correlate div id=game_split_tabs_* to ul class=player-tabs

    print datetime.now()-startTime 

if __name__ == '__main__':
    main()

# <div class="ez-spotlights">
# <div class="playerbio">
# <img src="http://static.nfl.com/static/content/public/image/getty/headshot/B/R/A/BRA371156.jpg"/>
# <p class="player">
# <a class="player" href="http://www.nfl.com/players/TomBrady/profile?id=BRA371156">Tom Brady</a>
# <span class="ez-bar">|</span>#12<span class="ez-bar">|</span>QB</p>
# <p class="team">
# <a class="team" href="http://www.nfl.com/teams/New England Patriots/profile?team=NE">New England Patriots</a>
# </p>
# <a class="profile" href="http://www.nfl.com/players/TomBrady/profile?id=BRA371156">Player Profile</a>
# <span class="ez-bar">|</span>
# <a class="stats" href="http://www.nfl.com/players/TomBrady/careerstats?id=BRA371156">Career Stats</a>
# <span class="ez-bar">|</span>
# <a class="logs" href="http://www.nfl.com/players/TomBrady/gamelogs?id=BRA371156">Game Logs</a>
# <span class="ez-bar">|</span>
# <a class="splits" href="http://www.nfl.com/players/TomBrady/gamesplits?id=BRA371156">Game Splits</a>
# <span class="ez-bar">|</span>
# <a class="sitstats" href="http://www.nfl.com/players/TomBrady/situationalstats?id=BRA371156">Situational Stats</a>
# <div class="ez-clearingDiv"> </div>
# </div></div>