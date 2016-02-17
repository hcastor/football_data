import argparse
import os
import time
from datetime import datetime

parser = argparse.ArgumentParser(description='Provide folder to watch')
parser.add_argument('-path', metavar='path', type=str, help='folder path to watch')

args = parser.parse_args()
path = args.path

filePosition = {}
fileMTime = {}
messages = []

while True:
    print 'gathering files'
    files = [fileName for fileName in os.listdir(path) if fileName[-4:] == '.log']
    for fileName in files:
        if fileName not in filePosition:
            filePosition[fileName] = 0
            fileMTime[fileName] = os.path.getmtime(os.path.join(path, fileName))
        elif fileMTime[fileName] == os.path.getmtime(os.path.join(path, fileName)):
            continue

        with open(os.path.join(path, fileName), 'rb') as log:
            log.seek(filePosition[fileName])
            for line in log:
                print fileName, '|$|', line,
                time.sleep(.25)
            filePosition[fileName] = log.tell()
        time.sleep(.35)
    time.sleep(1)