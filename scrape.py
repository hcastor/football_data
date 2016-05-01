#Date created 4/30/16
import sys
from datetime import datetime
from multiprocessing import Pool

from logWrapper import makeLogger, closeLogger
sys.path.append('./scrapers')
import getNFLPlayerStats
import getPFRSchedule
import getNFLTeamStats
import getNFLWeather
import getRotoFDStats

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

    pfrSchedule = pool.apply_async(getPFRSchedule.run, ())
    nflTeamStats = pool.apply_async(getNFLTeamStats.run, ())
    rotoFDStats = pool.apply_async(getRotoFDStats.run, ())

    nflWeather_started = False
    nflPlayerStats_started = False
    while not nflWeather_started or not nflPlayerStats_started:
        if not nflWeather_started and pfrSchedule.ready():
            if pfrSchedule.successful():
                nflWeather = pool.apply_async(getNFLWeather.run, ())
            else:
                print 'pfrSchedule not successful, skipping nflWeather'
            nflWeather_started = True

        if not nflPlayerStats_started and nflTeamStats.ready():
            if nflTeamStats.successful():
                nflPlayerStats = pool.apply_async(getNFLPlayerStats.run, (5400,))
            else:
                print 'nflTeamStats not successful, skipping nflPlayerStats'
            nflPlayerStats_started = True

    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    print datetime.now()-startTime

if __name__ == '__main__':
    main()