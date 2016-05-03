#Date created 2/27/16
import json
from robobrowser import RoboBrowser
from multiprocessing import Pool

def testProxy(proxy):
    """
    Tests a proxy with api.ipify.org
    If the proxy fails, it retries 20 more times.
    This is because free proxies are unreliable at times.
    """
    tries = 0
    browser = RoboBrowser(history=False,  parser='html5lib', timeout=10)
    while(True):
        try:
            tries += 1
            browser.open("http://api.ipify.org", proxies={'http': proxy})
            if browser.find('body').text != row['IP Address']:
                raise Exception('Failed')
            return row
        except:
            if tries > 20:
                return None

def main():
    """
    Used to get rid of any proxies that dont work anymore.
    Uses multiprocess to test 200 proxies at a time
    Overwrites proxy_list_http.csv with only working proxies
    """
    pool = Pool(processes=200)

    results = []
    with open('proxy_list_http.json', 'rb') as jsonData:
        proxies = json.load(jsonData)
        
        for proxy in proxies:
            #print testProxy(row)
            results.append(pool.apply_async(testProxy, (proxy,)))
    
    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    proxySet = set()
    duplicates = 0
    failed = 0
    success = 0
    with open('proxy_list_http.json', 'wb') as jsonFile:
        for result in results:
            proxy = result.get()
            if proxy:
                success += 1
                if proxy not in proxySet:
                    proxySet.add(proxy)
                else:
                    duplicates += 1
            else:
                failed += 1

        jsonFile.write(json.dumps(list(proxySet)))

    print 'success:', success
    print 'failed:', failed
    print 'duplicates:', duplicates
    print 'total:', success - duplicates

if __name__ == '__main__':
    main()