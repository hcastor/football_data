import time
import random
import csv
from robobrowser import RoboBrowser
from datetime import datetime

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

            if browser.response.status_code != 200:
                raise Exception('Response Code: ' + str(browser.response.status_code))
        except:
            logger.debug(action + ', tries: ' + str(tries))
            if tries > 20:
                tries = 0.1
                logger.exception('20 tries in a row, waiting 5 minutes')
                time.sleep(300)
            else:
                time.sleep(random.uniform(.5, 2.5))
            continue
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