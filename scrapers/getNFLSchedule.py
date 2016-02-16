#date create 2/13/16
#Populates schedule, and game info collections. Game info will have lot of duplicate data between weather and stadium
import re
import csv
import logging
import time
import random
from robobrowser import RoboBrowser
from datetime import datetime, timedelta
from pymongo import MongoClient
from multiprocessing import Pool

def makeLogger(loggerName, logDir):
    loggerName = str(loggerName)
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)
    timeStamp = datetime.now().strftime("_%Y-%m-%d_%H-%M-%S")
    debug_file_name = logDir + 'debug_' + loggerName + timeStamp + '.log'
    error_file_name = logDir + 'error_'+ loggerName + timeStamp +'.log'
    dfh = logging.FileHandler(debug_file_name)
    dfh.setLevel(logging.DEBUG)
    efh = logging.FileHandler(error_file_name)
    efh.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    efh.setFormatter(formatter)
    dfh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(efh)
    logger.addHandler(dfh)
    return logger

def closeLogger(loggerName):
    loggerName = str(loggerName)
    logger = logging.getLogger(loggerName)
    handlers = logger.handlers[:]
    while len(handlers):
        for handler in handlers:
            handler.close()
            logger.removeHandler(handler)
        handlers = logger.handlers[:]

def open_or_follow_link(logger, browser, action, url):
    """
    Wraps browser.open and browser.follow_link
    using a randome proxy per request
    tries 20 times to succend, else waits 5 minutes.
    returns browser
    should abstract out 20 and 300, also have max number of wait and retries
    """
    startTime = datetime.now()
    tries = 0
    while True:
        try:
            tries += 1
            if action.lower() == 'open':
                browser.open(url, proxies={'http': get_proxy(logger)})
            elif action.lower() == 'follow_link':
                browser.follow_link(url, proxies={'http': get_proxy(logger)})
        except:
            logger.debug(action + ', tries: ' + str(tries))
            if tries < 20:
                continue
            else:
                logger.exception(action + ', tries: ' + str(tries))
                time.sleep(300)
        logger.debug('open_or_follow_link time elapsed: ' + str(datetime.now() - startTime))
        return browser

def get_proxy(logger):
    """
    Reads ../proxy_list_http.csv and returns a random proxy.
    """
    proxies = []
    with open('../proxy_list_http.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            proxies.append('http://' + row['IP Address'] + ':' + row['Port'])

    index = random.randint(0,len(proxies)-1)

    logger.debug('Using proxy: %s', proxies[index])

    return proxies[index]

def get_proxy_count():
    """
    Reads ../proxy_list_http.csv and returns the total number of proxies.
    """
    count = 0
    with open('../proxy_list_http.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            count += 1

    return count

def get_user_agent(logger):
    """
    Returns a random user_agent
    """
    user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
        'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
        'Mozilla/5.0 (BlackBerry; U; BlackBerry 9900; en) AppleWebKit/534.11+ (KHTML, like Gecko) Version/7.1.0.346 Mobile Safari/534.11+',
        'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A']

    user_agent = user_agents[random.randint(0,7)]

    logger.debug('Using user_agent: %s', user_agent)

    return user_agent


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

    wait = random.uniform(1.5,3.5)
    logger.debug('Waiting %f', wait)
    time.sleep(wait)

    schedule_list = []
    gameInfo_list = []
    
    client = MongoClient('localhost', 27017)
    db = client['fantasy']
    col_nfl_schedule = db['nfl_schedule']
    col_game_info = db['game_info']

    logger.debug('Opening main page')
    browser = RoboBrowser(history=False,  parser='html5lib', user_agent=get_user_agent(logger), timeout=15)
    browser = open_or_follow_link(logger, browser, 'open', "http://www.pro-football-reference.com/years/{}/games.htm".format(year))
    table = browser.find(id='games')
    for row in table.find_all('tr'):
        try:
            schedule_dict = {}
            gameInfo_dict = {}
            columns = row.find_all('td')
            if columns:
                schedule_dict['week'] = columns[0].text
                schedule_dict['day'] = columns[1].text
                schedule_dict['date'] = columns[2].text
                schedule_dict['year'] = year
                homeIndicator = columns[5].text
                if homeIndicator == '@':
                    schedule_dict['homeTeam'] = columns[6].text
                    schedule_dict['awayTeam'] = columns[4].text
                    schedule_dict['homeTeamScore'] = columns[8].text
                    schedule_dict['awayTeamScore'] = columns[7].text
                else:
                    schedule_dict['homeTeam'] = columns[4].text
                    schedule_dict['awayTeam'] = columns[6].text
                    schedule_dict['homeTeamScore'] = columns[7].text
                    schedule_dict['awayTeamScore'] = columns[8].text
                gameInfo_dict['week'] = columns[0].text
                gameInfo_dict['year'] = year
                wait = random.uniform(.5, 2.5)
                logger.debug('Waiting to follow_link %f', wait)
                time.sleep(wait)
                logger.debug('Following link')
                url = columns[3].find('a')
                if url:
                    browser = open_or_follow_link(logger, browser, 'follow_link', url)
                    game_info = browser.find(id="game_info")
                    if game_info:
                        for each in game_info.find_all('tr'):
                            pair = each.find_all('td')
                            if pair:
                                key = pair[0].text
                                value = pair[1].text
                                gameInfo_dict[key] = value

                schedule_list.append(schedule_dict)
                gameInfo_list.append(gameInfo_dict)
        except:
            logger.exception(row)

    logger.debug('nfl_schedule.inert_many')

    schedule_ids = col_nfl_schedule.insert_many(schedule_list).inserted_ids
    
    logger.debug('mapping nfl_schedule.id to gameInfo_list')

    for index, schedule_id in enumerate(schedule_ids):
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

    pool = Pool(processes=get_proxy_count()/2)

    for i in range(maxyear-minyear+1):
        year = minyear + i
        #parseYear(year)
        pool.apply_async(parseYear, (year,))

    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    print datetime.now()-startTime 

if __name__ == '__main__':
    main()