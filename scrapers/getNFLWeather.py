#date create 2/13/16
import sys
import re
import random
import time
from robobrowser import RoboBrowser
from pymongo import MongoClient
from datetime import datetime, timedelta
from multiprocessing import Pool

from robobrowserWrapper import open_or_follow_link, get_proxy_count, get_user_agent
sys.path.append('../')
from logWrapper import makeLogger, closeLogger
from utilities import convertToNumber, cleanKey

client = MongoClient('localhost', 27017)
db = client['nfl_data']
col_schedule = db['schedule']
col_weather_info = db['weather_info']
col_stadium_info = db['stadium_info']

def parseWeek(year, week):
    """Parsing a specific week at http://nflweather.com/week/{}/Week-{}
    Follows all detial links, which is where must of the data is scraped.
    Scrapes weather, and stadium enough per week, and stores them in their respective collections
    """
    logger = makeLogger(str(year) + '_' + str(week), r'./logs_nflWeather/')

    startTime = datetime.now()

    logger.debug('Starting %d %d', year, week)

    weather_list = []
    stadium_list = []

    if col_weather_info.find({'year': year, 'week': week}).count():
        logger.debug('Already parsed %d %d', year, week)
        return None

    wait = random.uniform(1.5,3.5)
    logger.debug('Waiting %f', wait)
    time.sleep(wait)

    logger.debug('Opening main page')
    browser = RoboBrowser(history=False,  parser='html5lib', user_agent=get_user_agent(logger), timeout=10)
    browser = open_or_follow_link(logger, browser, 'open', "http://nflweather.com/week/{}/Week-{}".format(year, week))

    data = browser.find(class_="footable")
    rows = data.find_all('tr')

    for index, row in enumerate(rows):
        logger.debug('Row %d of %d', index, len(rows))
        weatherInfo = {'year': year, 'week': week}
        stadiumInfo = {'year': year, 'week': week}

        try:
            columns = row.find_all('td')
            if columns:
                weatherInfo['weatherPicAlt'] = columns[8].find('img')['alt']
                weatherInfo['weatherText'] = columns[9].text.strip()
                weatherInfo['shortWind'] = columns[10].text
                details = columns[12]
                detialsLink = 'http://nflweather.com' + details.find('a')['href']
                wait = random.uniform(.5, 2.5)
                logger.debug('Waiting to follow_link %f', wait)
                time.sleep(wait)
                logger.debug('Following link')
                browser = open_or_follow_link(logger, browser, 'open', detialsLink)
                gameTime = browser.find('strong').text.split('-')[0].split(':', 1)[1].strip()
                awayTeam = browser.find_all(class_='g-away')[1].find('a').text.replace('  ', ' ').strip()
                homeTeam = browser.find_all(class_='g-home')[1].find('a').text.replace('  ', ' ').strip()
                spans = browser.find_all(class_='span5')
                if len(spans) != 2:
                    raise Exception('to many spans')

                weatherItems = spans[0].find_all('p')
                stadiumItems = spans[1].find_all('p')

                index = spans[0].text.find('Temperature:')
                weatherCondition = spans[0].text[:index].strip()

                for each in weatherItems:
                    split = each.text.strip().split(':')
                    if len(split) == 2:
                        weatherInfo[cleanKey(split[0].strip())] = convertToNumber(split[1].strip())
                
                for index, each in enumerate(stadiumItems):
                    split = each.text.strip().split(':')
                    if len(split) == 2:
                        if split[0] == 'Surface':
                            stadiumInfo['stadium'] = stadiumItems[index-1].text.strip()
                        stadiumInfo[cleanKey(split[0].strip())] = convertToNumber(split[1].strip())

                #find nfl_schedule, update gameTime, hoepfully result as id, insert id into both info dicts, append to _list
                schedule_query = {'year': year, 'week': week, 'homeTeam': homeTeam, 'awayTeam': awayTeam}
                schedule_doc = col_schedule.find(schedule_query)
                if schedule_doc.count() != 1:
                    error_docs = str(schedule_query) + ' | ' + str(weatherInfo) + ' | ' + str(stadiumInfo)
                    raise Exception("nfl_scedule doc not found " + error_docs)
                result = col_schedule.update_one(schedule_query, {'$set': {'dateTime': gameTime}})
                schedule_id = schedule_doc[0]['_id']
                weatherInfo['schedule_id'] = schedule_id
                stadiumInfo['schedule_id'] = schedule_id
                weather_list.append(weatherInfo)
                stadium_list.append(stadiumInfo)
        except:
            logger.exception(row)

    try:
        logger.debug('Bulk Creating weather_list')
        col_weather_info.insert_many(weather_list)
        logger.debug('Bulk Creating stadium_list')
        col_stadium_info.insert_many(stadium_list)
    except:
        logger.exception('insert_many error')
    logger.debug('parseWeek time elapsed: ' + str(datetime.now() - startTime))

    closeLogger(str(year) + '_' + str(week))

def run(wait):
    """Starts the scrapping proccess.
    creates a process for each week per year given in pages
    """

    logger = makeLogger('main', r'./logs_nflWeather/')
    
    startTime = datetime.now()
    
    logger.debug('start time: ' + str(startTime))
    logger.debug('waiting %d seconds', wait)
    time.sleep(wait)

    pool = Pool(processes=int(get_proxy_count()/2.5))

    #nflweather.com goes back to 2009, 2010 seems to be missing.
    pages = [(2009, 17), (2010, 17), (2011, 17), (2012, 17), (2013, 17), (2014, 17), (2015, 17)]

    headers = []
    dataList = []
    for year, maxWeek in pages:
        for week in range(1, maxWeek+1):
            #parseWeek(year, week)
            pool.apply_async(parseWeek, (year, week,))

    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    logger.debug('run time: ' + str(datetime.now()-startTime ))

    closeLogger('main')