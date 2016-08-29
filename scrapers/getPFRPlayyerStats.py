#date create 8/28/16
#Populates schedule, and game info collections. Game info will have lot of duplicate data between weather and stadium
#db.getCollection('nfl_schedule').remove({ 'date': 'Playoffs' }) to remove empty Playoff lines
#game_info
import string



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

def parseTable(logger, pfr_player_bio_id, table, season_type):
    game_stat_dicts = []
    career_total_dict = {
        'pfr_player_bio_id': pfr_player_bio_id,
        'season_type': season_type
    }

    logger.debug('Parsing ' + season_type)
    games = table.find('tbody').find_all('tr')
    for game in games:
        game_stats = {}
        #skips over class='thead' rows since only has th's
        values = game.find_all('td')
        for column_index, value_object in enumerate(values):
            key = cleanKey(value_object['data-stat'])
            if value_object.text == '':
                value = 0
            elif key == 'game_date':
                value = datetime.strptime(value_object.text, '%Y-%m-%d')
            else:
                value = convertToNumber(value_object.text)
            
            #key scoring not accurate when kicker didnt attempt any FG but hasd XP
            game_stats[key] = value
        if not game_stats:
            continue

        game_stats['pfr_player_bio_id'] = pfr_player_bio_id
        game_stats['season_type'] = season_type
        game_stat_dicts.append(game_stats)


    logger.debug('Parsing totals ' + season_type)
    career_totals = table.find('tfoot').find('tr').find_all('td')
    for career_total in career_totals:
        key = cleanKey(career_total['data-stat'])
        value = convertToNumber(career_total.text)
        if not value:
            continue
        career_total_dict[key] = value

    return game_stat_dicts, career_total_dict


def parsePlayer(player_name, player_url):
    player_url = "http://www.pro-football-reference.com" + player_url

    logger = makeLogger(player_name, r'./logs_pfrPlayerStats/')

    startTime = datetime.now()
    
    logger.debug('start time: ' + str(startTime))

    client = MongoClient('localhost', 27017)
    db = client['nfl_data']
    col_pfr_player_bio = db['pfr_player_bio']
    col_pfr_player_game_stats = db['pfr_player_game_stats']
    col_pfr_player_career_stats = db['pfr_player_career_stats']

    if col_pfr_player_bio.find({'player_url': player_url}).count():
        logger.debug('Player already parsed ' + player_url)
        return

    wait = random.uniform(1.5,3)
    logger.debug('Waiting %f', wait)
    time.sleep(wait)
    
    logger.debug('Opening player page %s', player_url)
    browser = RoboBrowser(history=False,  parser='html5lib', user_agent=get_user_agent(logger), timeout=10)
    browser = open_or_follow_link(logger, browser, 'open', player_url + '/gamelog')

    logger.debug('Parsing player meta')
    meta_div = browser.find(id="meta")
    meta_items = None
    for div in meta_div.find_all('div'):
        try:
            if div['itemtype'] == 'http://schema.org/Person':
                meta_items = div.find_all('p')
        except KeyError:
            pass

    player_bio = {
        'player_url': player_url,
        'player_name': player_name
    }
    for meta_item in meta_items:
        physical_stat_row = False
        item_spans = meta_item.find_all('span')
        for item_span in item_spans:
            try:
                if item_span['itemprop'] == 'height':
                    physical_stat_row = True
                    player_bio['height'] = item_span.text
                elif item_span['itemprop'] == 'weight':
                    physical_stat_row = True
                    player_bio['weight'] = item_span.text
            except KeyError:
                pass

        if physical_stat_row:
            continue

        key_values = re.findall('([^:]+):([^:]+)(?: |$)', meta_item.text)
        for key, value in key_values:
            player_bio[cleanKey(key.replace(u'\xa0', u' '))] = value.strip().replace(u'\xa0', u' ')

    try:
        logger.debug('Creating player bio')
        player_bio_id = col_pfr_player_bio.insert(player_bio)
    except:
        logger.exception('insert error')
        return

    try:
        regular_season_div = browser.find(id='all_stats')
        regular_season_table = regular_season_div.find(class_="table_outer_container").find(id="div_stats")
    except AttributeError:
        logger.debug('No game logs, exiting player')
        return

    career_total_dicts = []
    try:
        game_stat_dicts, career_total_dict = parseTable(logger, player_bio_id, regular_season_table, 'regular season')
        career_total_dicts.append(career_total_dict)
    except:
        logger.exception('parseTable error. Deleting user bio and exiting')
        col_pfr_player_bio.remove({'player_url': player_url})
        return

    

    playoff_table = browser.find(id="stats_playoffs")
    if not playoff_table:
        logger.debug('No playoff game logs')
    else:
        try:
            temp_game_dicts, career_total_dict = parseTable(logger, player_bio_id, playoff_table, 'playoffs')
            game_stat_dicts += temp_game_dicts
            career_total_dicts.append(career_total_dict)
        except:
            logger.exception('parseTable error. Deleting user bio and exiting')
            col_pfr_player_bio.remove({'player_url': player_url})
            return
    
    try:
        logger.debug('Bulk Creating game_stat_dicts')
        if game_stat_dicts:
            col_pfr_player_game_stats.insert_many(game_stat_dicts)
        else:
            logger.debug('Nothing to insert')
    except:
        logger.exception('insert_many error')

    try:
        logger.debug('Bulk Creating career_total_dicts')
        if career_total_dict:
            col_pfr_player_career_stats.insert_many(career_total_dicts)
        else:
            logger.debug('Nothing to insert')
    except:
        logger.exception('insert_many error')

    logger.debug('parsePlayer time elapsed: ' + str(datetime.now() - startTime))

    closeLogger(logger)

def run(wait):
    """
    """
    logger = makeLogger('main', r'./logs_pfrPlayerStats/')

    startTime = datetime.now()
    
    logger.debug('start time: ' + str(startTime))
     
    browser = RoboBrowser(history=False,  parser='html5lib', user_agent=get_user_agent(logger), timeout=10)
    
    player_tuples = []
    for letter in list(string.ascii_uppercase):
        wait = random.uniform(.5,1.5)
        logger.debug('Waiting %f', wait)
        time.sleep(wait)

        logger.debug('Opening players %s', letter)
        browser = open_or_follow_link(logger, browser, 'open', "http://www.pro-football-reference.com/players/{}/".format(letter))
        players = browser.find(id="div_players")

        for player in players.find_all('p'):
            player = player.find('a')
            player_tuples.append((player.text, player['href']))

    pool = Pool(processes=int(get_proxy_count()/2.5))

    logger.debug('Processing %d Players', len(player_tuples))
    for player_tuple in player_tuples:
        #parsePlayer(player_tuple[0], player_tuple[1])
        pool.apply_async(parsePlayer, (player_tuple[0], player_tuple[1],))


    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    logger.debug('run time elapsed: ' + str(datetime.now() - startTime))

    closeLogger(logger)

if __name__ == '__main__':
    wait = 0
    if len(sys.argv) == 2:
        wait = int(sys.argv[1])
    run(wait)