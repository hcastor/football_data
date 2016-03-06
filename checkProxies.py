import csv
from robobrowser import RoboBrowser
from multiprocessing import Pool

def testProxy(row):
    tries = 0
    browser = RoboBrowser(history=False,  parser='html5lib', timeout=10)
    while(True):
        try:
            tries += 1
            browser.open("http://api.ipify.org", proxies={'http': 'http://' + row['IP Address'] + ':' + row['Port']})
            if browser.find('body').text != row['IP Address']:
                raise Exception('Failed')
            return row
        except:
            if tries > 20:
                return None

def main():
    pool = Pool(processes=200)


    results = []
    with open('proxy_list_http.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            #print testProxy(row)
            results.append(pool.apply_async(testProxy, (row,)))
    
    pool.close() #Prevents any more tasks from being submitted to the pool. Once all the tasks have been completed the worker processes will exit.
    pool.join() #Wait for the worker processes to exit. One must call close() or terminate() before using join().

    proxySet = set()
    duplicates = 0
    failed = 0
    success = 0
    with open('proxy_list_http.csv', 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Last Update','IP Address','Port','Country','Speed','Connection Time','Type','Anon'])
        writer.writeheader()
        for result in results:
            value = result.get()
            if value:
                success += 1
                proxy = value['IP Address'] + ' ' + value['Port']
                if proxy not in proxySet:
                    writer.writerow(value)
                    proxySet.add(proxy)
                else:
                    duplicates += 1
            else:
                failed += 1

    print 'success:', success
    print 'failed:', failed
    print 'duplicates:', duplicates
    print 'total:', success - duplicates

if __name__ == '__main__':
    main()