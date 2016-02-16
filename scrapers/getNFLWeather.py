#date create 2/13/16
import re
import csv
from robobrowser import RoboBrowser
from datetime import datetime, timedelta


def main():

	startTime = datetime.now()
	print startTime

	browser = RoboBrowser(history=False, parser='html5lib')

	#pages = [(2009, 17), (2010, 17), (2011, 17), (2012, 17), (2013, 17), (2014, 17), (2015, 17)]
	pages = [(2015, 17)]
	headers = []
	dataList = []
	for year, maxWeek in pages:
		for week in range(1, maxWeek+1):
			browser.open("http://nflweather.com/week/{}/Week-{}".format(year, week))

			data = browser.find(class_="footable")

			rows = data.find_all('tr')

			for row in rows:
				columns = row.find_all('td')
				if columns:
					awayTeam = columns[1]
					homeTeam = columns[5]
					weatherPic = columns[8]
					weatherText = columns[9]
					wind = columns[10]
					details = columns[12]
					print '-'*100
					print awayTeam.find('a').text
					print '-'*100
					print homeTeam.find('a').text
					print '-'*100
					print weatherPic.find('img')['alt']
					print '-'*100
					print weatherText.text.strip()
					print '-'*100
					print wind.text
					print '-'*100
					print details.find('a')['href']
					ok = 'http://nflweather.com' + details.find('a')['href']
					browser.open(ok)
					gameTime = browser.find('strong').text.split('-')[0].split(':', 1)[1].strip()
					print gameTime
					spans = browser.find_all(class_='span5')
					if len(spans) != 2:
						raise('to many spans')
					weatherItems = spans[0].find_all('p')
					stadiumItems = spans[1].find_all('p')
					print weatherItems[0].find('img')['alt']
					index = spans[0].text.find('Temperature:')
					print spans[0].text[:index].strip()
					for each in weatherItems:
						split = each.text.strip().split(':')
						if len(split) == 2:
							print split[0], split[1]
					
					for index, each in enumerate(stadiumItems):
						split = each.text.strip().split(':')
						if len(split) == 2:
							if split[0] == 'Surface':
								print stadiumItems[index-1].text
							print split[0], split[1]
				raw_input('-->')
			raw_input('-->')
	print datetime.now()-startTime 

if __name__ == '__main__':
	main()