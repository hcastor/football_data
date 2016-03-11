#Date created 10/25/15
import sys
import time
import random
from pymongo import MongoClient
from robobrowser import RoboBrowser
from datetime import datetime
from multiprocessing import Pool

from robobrowserWrapper import open_or_follow_link, get_proxy_count, get_user_agent
sys.path.append('../')
from logWrapper import makeLogger, closeLogger
from utilities import convertToNumber, cleanKey

def parseWeek(year, week):
    """
    parses a specific week on http://rotoguru1.com/cgi-bin/fyday.pl?week={}&year={}&game=fd&scsv=1
    which contains a csv of the fan duel player prices
    stores this info in fanduel_prices collection
    """
    logger = makeLogger(str(year) + '_' + str(week), r'./logs_RotoFDStats/')

    startTime = datetime.now()

    logger.debug('Starting %d', year)

    client = MongoClient('localhost', 27017)
    db = client['fantasy']
    col_fanduel_prices = db['fanduel_prices']

    if col_fanduel_prices.find({'year': year, 'week': week}).count():
        logger.debug('Already parsed %d %d', year, week)
        closeLogger(logger)
        return None

    wait = random.uniform(1.5,3.5)
    logger.debug('Waiting %f', wait)
    time.sleep(wait)

    logger.debug('Opening main page')
    browser = RoboBrowser(history=False, user_agent=get_user_agent(logger), timeout=10)
    url = "http://rotoguru1.com/cgi-bin/fyday.pl?week={}&year={}&game=fd&scsv=1".format(week, year)
    browser = open_or_follow_link(logger, browser, 'open', url)

    docs = []
    try:
        data = browser.find('pre').text
        lines = data.split('\n')
        header = lines[0]
        header = header.split(';')
        lines = lines[1:]
        for line in lines:
            doc = {}
            if not line:
                continue
            for index, each in enumerate(line.split(';')):
                doc[cleanKey(header[index])] = convertToNumber(each)
            docs.append(doc)
    except:
        logger.exception("Parse fail: %s", url)
    
    try:
        logger.debug('Bulk Creating docs')
        col_fanduel_prices.insert_many(docs)
    except:
        logger.exception('insert_many error')

    logger.debug('parseWeek time elapsed: ' + str(datetime.now() - startTime))

    closeLogger(str(year) + '_' + str(week))


def main():

    startTime = datetime.now()
    print startTime

    pool = Pool(processes=int(get_proxy_count()/2))

    pages = [(2011, 17), (2012, 17), (2013, 17), (2014, 17), (2015, 17)]
        
    for year, maxWeek in pages:
        for week in range(1, maxWeek+1):
            #parseWeek(year, week)
            pool.apply_async(parseWeek,(year, week,))

    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    print datetime.now()-startTime 

if __name__ == '__main__':
    main()