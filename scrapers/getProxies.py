from robobrowser import RoboBrowser

browser = RoboBrowser(history=False,  parser='html5lib')

browser.open('http://proxylist.hidemyass.com/search-1308503')

print browser.find(id='listable')