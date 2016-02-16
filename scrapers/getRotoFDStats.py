#Date created 10/25/15
import re
import csv
from robobrowser import RoboBrowser
from datetime import datetime, timedelta


def main():

	startTime = datetime.now()
	print startTime

	browser = RoboBrowser(history=False,  parser='html.parser')

	pages = [(2011, 17), (2012, 17), (2013, 17), (2014, 17), (2015, 17)]
		
	headers = []
	dataList = []
	for year, maxWeek in pages:
		for week in range(1, maxWeek+1):
			browser.open("http://rotoguru1.com/cgi-bin/fyday.pl?week={}&year={}&game=fd&scsv=1".format(week, year))

			data = browser.find('pre')
			headers.append(data.text[:56].replace(';', ','))
			dataList.append(data.text[57:].replace(';', ','))

	if any(x != 'Week;Year;GID;Name;Pos;Team;h/a;Oppt;FD points;FD salary'.replace(';', ',') for x in headers):
		print 'HEADER ERROR'
		return -1
	else:
		print "perfect"

	outputFile = open(r"./rotoFDStats.csv", 'w')
	outputFile.write(headers[0] + '\n')
	outputFile.close()

	for data in dataList:
		with open(r"./rotoFDStats.csv", 'a+') as outputFile:
			outputFile.write(data)


	print datetime.now()-startTime 

if __name__ == '__main__':
	main()