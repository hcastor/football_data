#Date created 10/25/15
import re
import csv
from robobrowser import RoboBrowser
from datetime import datetime, timedelta

def parseWeek(year, week):
    docs = []

    browser = RoboBrowser(history=False,  parser='html.parser')
    browser.open("http://rotoguru1.com/cgi-bin/fyday.pl?week={}&year={}&game=fd&scsv=1".format(week, year))

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
            doc[header[index]] = each
        docs.append(doc)

def main():

    startTime = datetime.now()
    print startTime

    pages = [(2011, 17), (2012, 17), (2013, 17), (2014, 17), (2015, 17)]
        
    for year, maxWeek in pages:
        for week in range(1, maxWeek+1):
            parseWeek(year, week)

    print datetime.now()-startTime 

if __name__ == '__main__':
    main()