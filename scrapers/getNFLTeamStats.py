#Date created 11/3/15
import re
import csv
import json
from collections import defaultdict
from robobrowser import RoboBrowser
from datetime import datetime, timedelta

def main():

    startTime = datetime.now()
    print startTime

    #html5lib parser required for broken html on gameSplits
    browser = RoboBrowser(history=False, parser='html5lib')

    browser.open("http://www.nfl.com/stats/categorystats?tabSeq=2&offensiveStatisticCategory=GAME_STATS&conference=ALL&role=TM&season=2015&seasonType=REG&d-447263-s=TOTAL_YARDS_GAME_AVG&d-447263-o=2&d-447263-n=1")

    #get form and form options
    form = browser.get_form(action="/stats/categorystats")
    role = browser.find(id="role")
    roles = role.find_all("option")
    offensiveCategory = browser.find(id="offensive-category")
    offensiveCategories = offensiveCategory.find_all("option")
    defensiveCategory = browser.find(id="defensive-category")
    defensiveCategories = defensiveCategory.find_all("option")
    season = browser.find(id="season-dropdown")
    seasons = season.find_all("option")
    seasonType = browser.find(id="season-type")
    seasonTypes = seasonType.find_all("option")

    teamStatDict = defaultdict(dict)
    for role in roles:
        print role['value']
        availableCategories = None
        if role.text == "Offense":
            availableCategories = offensiveCategories
        elif role.text == "Defense":
            availableCategories = defensiveCategories
        else:
            print "unknown role"

        for category in availableCategories:
            if category.text == "Category...":
                continue
            print category['value']
            for season in seasons:
                if season.text == "Season...":
                    continue
                print season['value']
                for seasonType in seasonTypes:
                    if seasonType.text == "Season Type...":
                        continue
                    print seasonType['value']
                    form["role"].value = role['value']
                    if role.text == "Offense":
                        form['offensiveStatisticCategory'].value = category['value']
                    elif role.text == "Defense":
                        form['defensiveStatisticCategory'].value = category['value']
                    form['season'].value = season['value']
                    form['seasonType'].value = seasonType['value']
                    browser.submit_form(form)
                    result = browser.find(id="result")
                    if result:
                        tbodies = result.find_all("tbody")
                        if len(tbodies) != 2:
                            print "error parsing result"
                        tableKey = tbodies[0]
                        tableKey = tableKey.find_all("th")

                        tableItems = tbodies[1]
                        tableItems = tableItems.find_all("td")

                        team = None
                        tableColumn = 0
                        for tableItem in tableItems:
                            if tableColumn == 0:
                                tableColumn += 1
                                continue

                            if tableColumn == 1:
                                team = tableItem.text
                                tableColumn += 1
                                continue

                            teamStatHashTuple = (re.sub('[\t,\n,\r]', '', team), re.sub('[\t,\n,\r]', '', season.text), re.sub('[\t,\n,\r]', '', seasonType.text), re.sub('[\t,\n,\r]', '', role.text))
                            teamStatDict[teamStatHashTuple][re.sub('[\t,\n,\r]', '', tableKey[tableColumn].text)] = re.sub('[\t,\n,\r]', '', tableItem.text)

                            tableColumn += 1
                            if tableColumn >= len(tableKey):
                                tableColumn = 0
                    print teamStatDict
                    raw_input('-->')
    for keyTuple, categories in teamStatDict.iteritems():
        print keyTuple
        print categories
    print datetime.now()-startTime 

if __name__ == '__main__':
    main()
