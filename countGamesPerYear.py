#Date created 2/28/16
from pymongo import MongoClient
from collections import Counter

client = MongoClient('localhost', 27017)
db = client['fantasy']
col_nfl_schedule = db['nfl_schedule']
col_game_info = db['game_info']
col_failed_game_info = db['failed_game_info']
col_weather_info = db['weather_info']
col_stadium_info = db['stadium_info']
col_nfl_team_stats = db['nfl_team_stats']
col_fanduel_prices = db['fanduel_prices']

weatherCounter = Counter()
for each in col_weather_info.find():
    year = col_nfl_schedule.find({'_id': each['nfl_schedule_id']})[0]['year']
    weatherCounter[year] += 1

stadiumCounter = Counter()
for each in col_weather_info.find():
    year = col_nfl_schedule.find({'_id': each['nfl_schedule_id']})[0]['year']
    stadiumCounter[year] += 1

minyear = 1960
maxyear = 2015

gameCountDict = {}
for i in range(maxyear-minyear+1):
    year = minyear + i
    gameCount = col_nfl_schedule.find({'year': year}).count()
    print '-'*30
    print 'year:', year
    print 'gameCount:', gameCount
    print 'weatherCount:', weatherCounter.get(year)
    print 'stadiumCount:', stadiumCounter.get(year)

previous_year = None
for each in col_nfl_team_stats.aggregate([
        { "$group":{ '_id':{'year': '$year', 'role': '$role', 'category': '$category'}, 'count': {"$sum": 1}}},
        {'$sort':{'_id.year':1, '_id.role':-1}},

    ]):
    year = each['_id']['year']
    if previous_year != year:
        print '-'*30
        print 'year:', year
    #Count should be equal per year through categories
    print each['_id']['role'], each['_id']['category'], 'Count:', each['count']
    previous_year = year

for each in col_fanduel_prices.aggregate([
        {"$group":{ '_id': {'year': '$year', 'week': '$week'}, 'count': {"$sum": 1}}},
        {'$sort':{ '_id.week':-1, '_id.year':-1}},
        ]):
    print each
