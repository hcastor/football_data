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
from utilities import convertToInt

def parseYear(year):
    """
    parses a schedule for a specific year on http://www.pro-football-reference.com/years/{YEAR}/games.htm
    follows all the "boxscore" links (column[3]) to get stadium and weather conditions (game_info)
    stores schedule info in fantasy.nfl_schedule
    stores game_info in fantasy.game_info with nfl_schedule ids
    """
    logger = makeLogger(year, r'./logs_nflSchedule/')

    startTime = datetime.now()

    logger.debug('Starting %d', year)

    schedule_list = []
    gameInfo_list = []

    client = MongoClient('localhost', 27017)
    db = client['fantasy']
    col_nfl_schedule = db['nfl_schedule']
    col_game_info = db['game_info']

    if col_nfl_schedule.find({'year': year}).count():
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
                schedule_dict['week'] = convertToInt(columns[0].text)
                schedule_dict['day'] = columns[1].text
                schedule_dict['date'] = columns[2].text
                schedule_dict['year'] = convertToInt(year)
                homeIndicator = columns[5].text
                if homeIndicator == '@':
                    schedule_dict['homeTeam'] = columns[6].text
                    schedule_dict['awayTeam'] = columns[4].text
                    schedule_dict['homeTeamScore'] = convertToInt(columns[8].text)
                    schedule_dict['awayTeamScore'] = convertToInt(columns[7].text)
                else:
                    schedule_dict['homeTeam'] = columns[4].text
                    schedule_dict['awayTeam'] = columns[6].text
                    schedule_dict['homeTeamScore'] = convertToInt(columns[7].text)
                    schedule_dict['awayTeamScore'] = convertToInt(columns[8].text)
                gameInfo_dict['week'] = convertToInt(columns[0].text)
                gameInfo_dict['year'] = convertToInt(year)
                wait = random.uniform(.5, 2.5)
                logger.debug('Waiting to follow_link %f', wait)
                time.sleep(wait)
                logger.debug('Following link')
                url = columns[3].find('a')
                if url:
                    gameInfo_tries = 0
                    game_info = None
                    while not game_info:
                        gameInfo_tries += 1
                        if gameInfo_tries > 1:
                            logger.debug('game_info tries: %d', gameInfo_tries)
                        browser = open_or_follow_link(logger, browser, 'follow_link', url)
                        game_info = browser.find(id="game_info")
                        if game_info:
                            for each in game_info.find_all('tr'):
                                pair = each.find_all('td')
                                if pair:
                                    key = pair[0].text
                                    value = convertToInt(pair[1].text)
                                    gameInfo_dict[key] = value

                schedule_list.append(schedule_dict)
                gameInfo_list.append(gameInfo_dict)
        except:
            logger.exception(row)

    logger.debug('nfl_schedule.inert_many')

    schedule_ids = col_nfl_schedule.insert_many(schedule_list).inserted_ids
    
    logger.debug('mapping nfl_schedule.id to gameInfo_list')

    for index, schedule_id in enumerate(schedule_ids):
        if len(gameInfo_list[index].keys()) <= 2:
            logger.debug('Empty game_info: %s', schedule_id)
        gameInfo_list[index]['schedule_id'] = schedule_id

    logger.debug('game_info.insert_many')
    col_game_info.insert_many(gameInfo_list)

    logger.debug('parseYear time elapsed: ' + str(datetime.now() - startTime))

    closeLogger(year)

def main():

    startTime = datetime.now()
    print startTime

    minyear = 1960
    maxyear = 2015

    pool = Pool(processes=int(get_proxy_count()/2.5))

    for i in range(maxyear-minyear+1):
        year = minyear + i
        #parseYear(year)
        pool.apply_async(parseYear, (year,))

    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    print datetime.now()-startTime 

if __name__ == '__main__':
    main()