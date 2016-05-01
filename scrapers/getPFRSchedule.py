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

def parseYear(year):
    """
    parses a schedule for a specific year on http://www.pro-football-reference.com/years/{YEAR}/games.htm
    follows all the "boxscore" links (column[3]) to get stadium and weather conditions (game_info)
    stores schedule info in nfl_data.schedule
    stores game_info in nfl_data.game_info with schedule ids
    """
    logger = makeLogger(year, r'./logs_pfrSchedule/')

    startTime = datetime.now()

    logger.debug('Starting %d', year)

    schedule_list = []
    gameInfo_list = []

    client = MongoClient('localhost', 27017)
    db = client['nfl_data']
    col_schedule = db['schedule']
    col_game_info = db['game_info']
    col_failed_game_info = db['failed_game_info']

    if col_schedule.find({'year': year}).count():
        logger.debug('Already parsed %s', year)
        closeLogger(logger)
        return None

    wait = random.uniform(1.5,3.5)
    logger.debug('Waiting %f', wait)
    time.sleep(wait)

    logger.debug('Opening main page')
    browser = RoboBrowser(history=False,  parser='html5lib', user_agent=get_user_agent(logger), timeout=10)
    browser = open_or_follow_link(logger, browser, 'open', "http://www.pro-football-reference.com/years/{}/games.htm".format(year))
    table = browser.find(id='games')
    rows = table.find_all('tr')
    for index, row in enumerate(rows):
        logger.debug('Row %d of %d', index, len(rows))
        try:
            schedule_dict = {}
            gameInfo_dict = {}
            columns = row.find_all('td')
            if columns:
                schedule_dict['week'] = convertToNumber(columns[0].text)
                schedule_dict['day'] = columns[1].text
                schedule_dict['date'] = columns[2].text
                schedule_dict['year'] = convertToNumber(year)
                homeIndicator = columns[5].text
                if homeIndicator == '@':
                    schedule_dict['homeTeam'] = columns[6].text
                    schedule_dict['awayTeam'] = columns[4].text
                    schedule_dict['homeTeamScore'] = convertToNumber(columns[8].text)
                    schedule_dict['awayTeamScore'] = convertToNumber(columns[7].text)
                else:
                    schedule_dict['homeTeam'] = columns[4].text
                    schedule_dict['awayTeam'] = columns[6].text
                    schedule_dict['homeTeamScore'] = convertToNumber(columns[7].text)
                    schedule_dict['awayTeamScore'] = convertToNumber(columns[8].text)
                gameInfo_dict['week'] = convertToNumber(columns[0].text)
                gameInfo_dict['year'] = convertToNumber(year)
                wait = random.uniform(.5, 2.5)
                logger.debug('Waiting to follow_link %f', wait)
                time.sleep(wait)
                logger.debug('Following link')
                url = columns[3].find('a')
                if url:
                    url = 'http://www.pro-football-reference.com' + url['href']
                    failed_game_info = True
                    browser = open_or_follow_link(logger, browser, 'open', url)
                    game_info = browser.find(id="game_info")
                    if game_info:
                        for each in game_info.find_all('tr'):
                            pair = each.find_all('td')
                            if pair:
                                failed_game_info = False
                                key = pair[0].text
                                value = convertToNumber(pair[1].text)
                                gameInfo_dict[cleanKey(key)] = convertToNumber(value)
                    if failed_game_info:
                        failed_dict = schedule_dict
                        failed_dict['row'] = index
                        failed_dict['href'] = url['href']
                        col_failed_game_info.insert(failed_dict)
                        gameInfo_dict['FAIL'] = True

                schedule_list.append(schedule_dict)
                gameInfo_list.append(gameInfo_dict)
        except:
            logger.exception(row)

    logger.debug('nfl_schedule.inert_many')

    schedule_ids = col_schedule.insert_many(schedule_list).inserted_ids
    
    logger.debug('mapping nfl_schedule.id to gameInfo_list')

    for index, schedule_id in enumerate(schedule_ids):
        if len(gameInfo_list[index].keys()) <= 2:
            logger.debug('Empty game_info: %s', schedule_id)
        gameInfo_list[index]['schedule_id'] = schedule_id

    logger.debug('game_info.insert_many')
    col_game_info.insert_many(gameInfo_list)

    logger.debug('parseYear time elapsed: ' + str(datetime.now() - startTime))

    closeLogger(year)

def run(wait):
    """Starts the scrapping proccess.
    creates a process per year between minyear and maxyear
    """

    logger = makeLogger('main', r'./logs_pfrSchedule/')

    startTime = datetime.now()
    
    logger.debug('start time: ' + str(startTime))
    logger.debug('waiting %d seconds', wait)
    time.sleep(wait)

    minyear = 1960
    maxyear = 2015

    pool = Pool(processes=int(get_proxy_count()/2))

    for i in range(maxyear-minyear+1):
        year = minyear + i
        #parseYear(year)
        pool.apply_async(parseYear, (year,))

    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    logger.debug('run time: ' + str(datetime.now()-startTime ))

    closeLogger('main')

if __name__ == '__main__':
    wait = 0
    if len(sys.argv) == 2:
        wait = sys.argv[1]
    run(wait)