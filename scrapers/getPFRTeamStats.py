#date create 2/13/16
#Populates schedule, and game info collections. Game info will have lot of duplicate data between weather and stadium
#db.getCollection('nfl_schedule').remove({ 'date': 'Playoffs' }) to remove empty Playoff lines
#game_info 
import re
import csv
import time
import random
import sys
from robobrowser import RoboBrowser
from datetime import datetime
from pymongo import MongoClient
from multiprocessing import Pool

from robobrowserWrapper import open_or_follow_link, get_proxy_count, get_user_agent
sys.path.append('../')
from logWrapper import makeLogger, closeLogger
from utilities import convertToNumber, cleanKey

def parseYear(team_name, year_url, year):
    """
    parses a schedule for a specific year on http://www.pro-football-reference.com/years/{YEAR}/games.htm
    follows all the "boxscore" links (column[3]) to get stadium and weather conditions (game_info)
    stores schedule info in nfl_data.schedule
    stores game_info in nfl_data.game_info with schedule ids
    """
    logger = makeLogger(cleanKey(team_name) + '_' + str(year), r'./logs_pfrTeamStats/')

    startTime = datetime.now()

    logger.debug('Starting %d', year)

    schedule_list = []
    gameInfo_list = []

    client = MongoClient('localhost', 27017)
    db = client['nfl_data']
    col_team_stats_weekly = db['team_stats_weekly']

    #need to fix this to actually detect duplicate
    # if col_team_stats_weekly.find({'year': year}).count():
    #     logger.debug('Already parsed %s', year)
    #     closeLogger(logger)
    #     return None

    wait = random.uniform(1.5,3.5)
    logger.debug('Waiting %f', wait)
    time.sleep(wait)

    logger.debug('Opening main page')
    browser = RoboBrowser(history=False,  parser='html5lib', user_agent=get_user_agent(logger), timeout=10)
    browser = open_or_follow_link(logger, browser, 'open', year_url)
    table = browser.find(id='games')
    rows = table.find_all('tr')
    header = [cleanKey(each.attrs['data-stat']) for each in rows[0].find_all('th')]
    rows = rows[1:]

    row_dicts = []
    for index, row in enumerate(rows):
        logger.debug('Row %d of %d', index, len(rows))
        try:
            week_number = convertToNumber(row.find('th').text)
            row_values = [convertToNumber(value.text) for value in row.find_all('td')]
            row_values.insert(0, week_number)
            row_dict = dict(zip(header, row_values))
            row_dict['year'] = year
            row_dict['team_name'] = team_name
            row_dict['year_url'] = year_url

            if row_dict['game_date'].lower() == 'playoffs':
                continue

            row_dicts.append(row_dict)
        except:
            logger.exception(row)

    logger.debug('team_stats_weekly.inert_many')

    col_team_stats_weekly.insert_many(row_dicts)

    logger.debug('parseYear time elapsed: ' + str(datetime.now() - startTime))

    closeLogger(logger)

def parseTeam(team_url, team_name):
    """
    parses a teams page returns a list of year urls
    there is some data on this page that would be usefull to scrape in the future
    """
    logger = makeLogger(cleanKey(team_name), r'./logs_pfrTeamStats/')

    startTime = datetime.now()

    logger.debug('Starting %s', team_name)

    wait = random.uniform(1.5,3.5)
    logger.debug('Waiting %f', wait)
    time.sleep(wait)

    logger.debug('Opening main page')
    browser = RoboBrowser(history=False,  parser='html5lib', user_agent=get_user_agent(logger), timeout=10)
    browser = open_or_follow_link(logger, browser, 'open', team_url)
    table = browser.find(id='team_index').find('tbody')
    year_columns = table.find_all('th')
    
    year_url_tups = []
    for index, year_column in enumerate(year_columns):
        logger.debug('Row %d of %d', index, len(year_columns))
        try:
            year_link = year_column.find('a')
            if year_link:
                year_url = 'http://www.pro-football-reference.com' + year_link['href']
                year = convertToNumber(year_link.text)
                if not isinstance(year, int):
                    continue
                year_url_tups.append((team_name, year_url, year))
        except:
            logger.exception(year_column)
 
    logger.debug('parseTeam time elapsed: ' + str(datetime.now() - startTime))

    closeLogger(logger)

    return year_url_tups



def run(wait):
    """Starts the scrapping proccess.
    creates a process per year between minyear and maxyear
    """

    logger = makeLogger('main', r'./logs_pfrTeamStats/')

    startTime = datetime.now()
    
    logger.debug('start time: ' + str(startTime))

    logger.debug('waiting %d seconds', wait)
    time.sleep(wait)

    logger.debug('Opening main page')
    browser = RoboBrowser(history=False,  parser='html5lib', user_agent=get_user_agent(logger), timeout=10)
    browser = open_or_follow_link(logger, browser, 'open', "http://www.pro-football-reference.com/teams/")
    table_body = browser.find(id='teams_active').find('tbody')
    rows = table_body.find_all('tr')

    team_url_tups = []

    for index, row in enumerate(rows):
        logger.debug('Row %d of %d', index, len(rows))
        try:
            team_link = row.find('th').find('a')
            if team_link:
                team_url = 'http://www.pro-football-reference.com' + team_link['href']
                team_name = team_link.text
                team_url_tups.append((team_url, team_name))
        except:
            logger.exception(row)

    pool = Pool(processes=int(get_proxy_count()/2.5))
    results = []

    for team_url, team_name in team_url_tups:
        #print parseTeam(team_url, team_name)
        results.append(pool.apply_async(parseTeam, (team_url, team_name,)))
    
    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    year_url_tups = []
    for result in results:
        year_url_tup = result.get()
        if year_url_tup:
            year_url_tups += (year_url_tup)

    logger.debug('Done gathering %d year urls', len(year_url_tups))

    pool = Pool(processes=int(get_proxy_count()/2))

    logger.debug('Shuffling year_urls')
    random.shuffle(year_url_tups)
    logger.debug('Starting to parse year_urls')
    for team_name, year_url, year in year_url_tups:
        #parseYear(team_name, year_url, year)
        pool.apply_async(parseYear, (team_name, year_url, year,))

    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    logger.debug('run time: ' + str(datetime.now()-startTime ))

    closeLogger('main')

if __name__ == '__main__':
    wait = 0
    if len(sys.argv) == 2:
        wait = int(sys.argv[1])
    run(wait)