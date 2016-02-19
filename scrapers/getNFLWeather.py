#date create 2/13/16
import re
import csv
from robobrowser import RoboBrowser
from datetime import datetime, timedelta

def parseWeek(year, week):
    logger = makeLogger(year, r'./logs_nflWeather/')

    startTime = datetime.now()

    logger.debug('Starting %d %d', year, week)

    weather_list = []
    stadium_list = []

    client = MongoClient('localhost', 27017)
    db = client['fantasy']
    col_weather_info = db['weather_info']
    col_stadium_info = db['stadium_info']

    if col_weather_info.find({'year': year, 'week': week}).count():
        logger.debug('Already parsed %d %d', year, week)
        return None

    wait = random.uniform(1.5,3.5)
    logger.debug('Waiting %f', wait)
    time.sleep(wait)

    logger.debug('Opening main page')
    browser = RoboBrowser(history=False,  parser='html5lib', user_agent=get_user_agent(logger), timeout=15)
    browser = open_or_follow_link(logger, browser, 'open', "http://nflweather.com/week/{}/Week-{}".format(year, week))

    data = browser.find(class_="footable")
    rows = data.find_all('tr')


    for row in rows:
        weatherInfo = {}
        stadiumInfo = {}

        columns = row.find_all('td')
        if columns:
            awayTeam = columns[1].find('a').text
            homeTeam = columns[5].find('a').text
            weatherInfo['weatherPicAlt'] = columns[8].find('img')['alt']
            weatherInfo['weatherText'] = columns[9].text.strip()
            weatherInfo['shortWind'] = columns[10].text
            details = columns[12]
            detialsLink = 'http://nflweather.com' + details.find('a')['href']
            browser = open_or_follow_link(logger, browser, 'open', detialsLink)
            gameTime = browser.find('strong').text.split('-')[0].split(':', 1)[1].strip()
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
                    weatherInfo['split[0].strip()'] = split[1].strip()
            
            for index, each in enumerate(stadiumItems):
                split = each.text.strip().split(':')
                if len(split) == 2:
                    if split[0] == 'Surface':
                        weatherInfo['stadium'] = stadiumItems[index-1].text.strip()
                    weatherInfo['split[0].strip()'] = split[1].strip()

            #find nfl_schedule, update gameTime, hoepfully result as id, insert id into both info dicts, append to _list
    #bulk create
    #close logger

def main():

    startTime = datetime.now()
    print startTime

    pool = Pool(processes=get_proxy_count()/2)

    #pages = [(2009, 17), (2010, 17), (2011, 17), (2012, 17), (2013, 17), (2014, 17), (2015, 17)]
    pages = [(2015, 17)]
    headers = []
    dataList = []
    for year, maxWeek in pages:
        for week in range(1, maxWeek+1):
            parseWeek(year, week)
            #pool.apply_async(parseWeek, (year, week,))

    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    print datetime.now()-startTime 

if __name__ == '__main__':
    main()