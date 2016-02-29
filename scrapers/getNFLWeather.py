#date create 2/13/16
import sys
import re
import csv
import random
import time
from robobrowser import RoboBrowser
from pymongo import MongoClient
from datetime import datetime, timedelta
from multiprocessing import Pool

from robobrowserWrapper import open_or_follow_link, get_proxy_count, get_user_agent
sys.path.append('../')
from logWrapper import makeLogger, closeLogger
from utilities import convertToInt

def parseWeek(year, week):
    logger = makeLogger(str(year) + '_' + str(week), r'./logs_nflWeather/')

    startTime = datetime.now()

    logger.debug('Starting %d %d', year, week)

    weather_list = []
    stadium_list = []

    client = MongoClient('localhost', 27017)
    db = client['fantasy']
    col_nfl_schedule = db['nfl_schedule']
    col_weather_info = db['weather_info']
    col_stadium_info = db['stadium_info']

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
        weatherInfo = {}
        stadiumInfo = {}

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
                    raise('to many spans')

                weatherItems = spans[0].find_all('p')
                stadiumItems = spans[1].find_all('p')

                index = spans[0].text.find('Temperature:')
                weatherCondition = spans[0].text[:index].strip()

                for each in weatherItems:
                    split = each.text.strip().split(':')
                    if len(split) == 2:
                        weatherInfo[split[0].strip()] = convertToInt(split[1].strip())
                
                for index, each in enumerate(stadiumItems):
                    split = each.text.strip().split(':')
                    if len(split) == 2:
                        if split[0] == 'Surface':
                            weatherInfo['stadium'] = stadiumItems[index-1].text.strip()
                        stadiumInfo[split[0].strip()] = convertToInt(split[1].strip())

                #find nfl_schedule, update gameTime, hoepfully result as id, insert id into both info dicts, append to _list
                nfl_schedule_query = {'year': year, 'week': week, 'homeTeam': homeTeam, 'awayTeam': awayTeam}
                nfl_schedule_doc = col_nfl_schedule.find(nfl_schedule_query)
                if nfl_schedule_doc.count() != 1:
                    error_docs = str(nfl_schedule_query) + ' | ' + str(weatherInfo) + ' | ' + str(stadiumInfo)
                    raise Exception("nfl_scedule doc not found " + error_docs)
                result = col_nfl_schedule.update_one(nfl_schedule_query, {'$set': {'dateTime': gameTime}})
                nfl_schedule_id = nfl_schedule_doc[0]['_id']
                weatherInfo['nfl_schedule_id'] = nfl_schedule_id
                stadiumInfo['nfl_schedule_id'] = nfl_schedule_id
                weather_list.append(weatherInfo)
                stadium_list.append(stadiumInfo)
        except:
            logger.exception(row)

    logger.debug('Bulk Creating weather_list')
    col_weather_info.insert_many(weather_list)
    logger.debug('Bulk Creating stadium_list')
    col_stadium_info.insert_many(stadium_list)

    logger.debug('parseWeek time elapsed: ' + str(datetime.now() - startTime))

    closeLogger(str(year) + '_' + str(week))

def main():

    startTime = datetime.now()
    print startTime

    pool = Pool(processes=int(get_proxy_count()/2.5))

    pages = [(2009, 17), (2010, 17), (2011, 17), (2012, 17), (2013, 17), (2014, 17), (2015, 17)]
    #pages = [(2015, 17)]
    headers = []
    dataList = []
    for year, maxWeek in pages:
        for week in range(1, maxWeek+1):
            #parseWeek(year, week)
            pool.apply_async(parseWeek, (year, week,))

    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    print datetime.now()-startTime 

if __name__ == '__main__':
    main()