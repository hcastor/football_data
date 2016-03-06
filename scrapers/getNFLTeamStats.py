#Date created 11/3/15
import sys
import re
import random
import time
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
col_nfl_team_stats = db['nfl_team_stats']

def removeNewLine(value):
    return re.sub('[\t,\n,\r]', '', value)

def parseSeason(role, category, season, seasonTypes):
    """Parses every seasonType in a season at http://www.nfl.com/stats/categorystats for a given role/category/season
    doesnt follow any links
    some years dont have any info, but still return a page.
    These are loged with Exception('No teams found %s' % url)
    All data is stored in nfl_team_stats
    """
    logger = makeLogger(role.text + '_' + category.text + '_' + season.text, r'./logs_nflteamStat/')

    startTime = datetime.now()

    logger.debug('Starting %s %s %s', role.text, category.text, season.text)

    teamStat_list = []
    for seasonType in seasonTypes:
        if seasonType.text == "Season Type...":
            continue

        team_stats_query = {'year': convertToNumber(removeNewLine(season.text)),
            'seasonType': removeNewLine(seasonType.text),
            'role': removeNewLine(role.text),
            'category': removeNewLine(category.text)
        }

        if col_nfl_team_stats.find(team_stats_query).count():
            logger.debug('Already parsed %s', team_stats_query)
            continue

        wait = random.uniform(1.5,3.5)
        logger.debug('Waiting %f', wait)
        time.sleep(wait)

        logger.debug('Starting: %s', team_stats_query)
        url = 'http://www.nfl.com/stats/categorystats?' + 'archive=true&conference=null' + '&role=' + role['value']
        try:
            if role.text == "Offense":
                categoryUrl = '&offensiveStatisticCategory=' + category['value'] + '&defensiveStatisticCategory=null'
                
            elif role.text == "Defense":
                categoryUrl = '&offensiveStatisticCategory=null&defensiveStatisticCategory=' + category['value']
            else:
                raise Exception('Unsupported role: %s', role.text)
            
            url += categoryUrl
            url += '&season=' + season['value'] + '&seasonType=' + seasonType['value'] + '&tabSeq=2&qualified=false&Submit=Go'

            logger.debug('Opening: %s', url)
            browser = RoboBrowser(history=False,  parser='html5lib', user_agent=get_user_agent(logger), timeout=10)
            browser = open_or_follow_link(logger, browser, 'open', url)
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
                    logger.debug('Row %d of %d', tableIndex, len(tableItems))
                    tableColumn += 1
                    continue

                if tableColumn == 1:
                    teamStatDict['team'] = removeNewLine(tableItem.text)
                    teamStatDict['year'] = convertToNumber(removeNewLine(season.text))
                    teamStatDict['seasonType'] = removeNewLine(seasonType.text)
                    teamStatDict['role'] = removeNewLine(role.text)
                    teamStatDict['category'] = removeNewLine(category.text)
                    tableColumn += 1
                    continue

                key = cleanKey(removeNewLine(tableKey[tableColumn].text))
                value = convertToNumber(removeNewLine(tableItem.text))
                teamStatDict[key] = value

                tableColumn += 1
                if tableColumn >= len(tableKey):
                    teamStat_list.append(teamStatDict)
                    teamStatDict = {}
                    tableColumn = 0
        except:
            logger.exception('row fail')

    try:
        if teamStat_list:
            logger.debug('Bulk Creating teamStat_list')
            col_nfl_team_stats.insert_many(teamStat_list)
    except:
        logger.exception('insert_many error')

    logger.debug('parseSeason time elapsed: ' + str(datetime.now() - startTime))

    closeLogger(role.text + '_' + category.text)

def main():
    """Starts the scrapping proccess.
    Opens a teamstats page and gathers all the form inputs
    Then sends these inputs to parseSeason which opens a new page for every possible option in the form
    If you get an error at the start, with role.find_all, just try again, nfl.com returns weird pages sometimes
    """

    logger = makeLogger('main', r'./logs_nflteamStat/')

    startTime = datetime.now()
    logger.debug('Starting')

    pool = Pool(processes=int(get_proxy_count()/2.5))

    #html5lib parser required for broken html on gameSplits
    browser = RoboBrowser(history=False,  parser='html5lib', user_agent=get_user_agent(logger), timeout=10)
    startingUrl = "http://www.nfl.com/stats/categorystats?tabSeq=2&offensiveStatisticCategory=GAME_STATS&conference=ALL&role=TM&season=2015&seasonType=REG"
    browser = open_or_follow_link(logger, browser, 'open', startingUrl)
    
    role = browser.find(id="role")
    roles = role.find_all("option")
    offensiveCategory = browser.find(id="offensive-category")
    offensiveCategories = offensiveCategory.find_all("option")
    defensiveCategory = browser.find(id="defensive-category")
    defensiveCategories = defensiveCategory.find_all("option")
    season = browser.find(id="season-dropdown")
    seasons = season.find_all("option")
    seasonType = browser.find(id="season-type")
    seasonTypes = seasonType.find_all("option")

    
    for role in roles:
        availableCategories = None
        if role.text == "Offense":
            availableCategories = offensiveCategories
        elif role.text == "Defense":
            availableCategories = defensiveCategories
        else:
            print "unknown role"

        for category in availableCategories:
            if category.text == "Category...":
                continue
            for season in seasons:
                if season.text == "Season..." or convertToNumber(removeNewLine(season.text)) < 1960:
                    continue
                #parseSeason(role, category, season, seasonTypes)
                pool.apply_async(parseSeason, (role, category, season, seasonTypes,))

    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    print datetime.now()-startTime
    logger.debug('main time elapsed: ' + str(datetime.now() - startTime))

if __name__ == '__main__':
    main()
