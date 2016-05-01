#Date created 4/30/16
import sys
import time
from datetime import datetime
from multiprocessing import Pool
from subprocess import Popen

from logWrapper import makeLogger, closeLogger
sys.path.append('./scrapers')
import getNFLPlayerStats
import getPFRSchedule
import getNFLTeamStats
import getNFLWeather
import getRotoFDStats

def run(scriptName, *args):
    cmd = 'python ' + scriptName
    for arg in args:
        cmd += ' ' + arg

    Popen(cmd, cwd=r'./scrapers').wait()

def main():
    """
    Starts all of the scrappers.
    It conditionally starts certain scrappers either for a mongo requirement, 
    or to prevent parsing the same site with two differtent parses at the same time.
    Optional argument, wait, can be past to .run to sleep n seconds before starting
    First starts getPFRSchedule, getNFLTeamStats, and getRotoFDStats
    Once getPFRSchedule is done, getNFLWeather is started
    Once getNFLTeamStats, getNFLPlayerStats is started
    """

    startTime = datetime.now()
    print startTime

    pool = Pool(processes=5)

    pfrSchedule = pool.apply_async(run, ('getPFRSchedule.py',))
    nflTeamStats = pool.apply_async(run, ('getNFLTeamStats.py',))
    rotoFDStats = pool.apply_async(run, ('getRotoFDStats.py',))

    nflWeather_started = False
    nflPlayerStats_started = False
    while not nflWeather_started or not nflPlayerStats_started:
        time.sleep(1)
        if not nflWeather_started and pfrSchedule.ready():
            if pfrSchedule.successful():
                nflWeather = pool.apply_async(run, ('getNFLWeather.py',))
            else:
                print 'pfrSchedule not successful, skipping nflWeather'
            nflWeather_started = True

        if not nflPlayerStats_started and nflTeamStats.ready():
            if nflTeamStats.successful():
                nflPlayerStats = pool.apply_async(run, ('getNFLPlayerStats.py', 5400,))
            else:
                print 'nflTeamStats not successful, skipping nflPlayerStats'
            nflPlayerStats_started = True

    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    print datetime.now()-startTime

if __name__ == '__main__':
    main()