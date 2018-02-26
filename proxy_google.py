import urllib
import time
import re
import string
import pymysql
import threading
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from zlib import crc32
import CommonFun



def checkHasProxy(brower):
  try:
    text = brower.find_element_by_css_selector('body').text
    result =re.findall(r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)[:| ][1-9][0-9]+", text)
    if len(result) > 0:
        return result
  except :
    pass
  return False

def getPageAllLink(browser):
  items = browser.find_elements_by_css_selector('a')
  current = browser.current_url
  parse = urllib.parse.urlparse(current)
  host = parse.netloc
  result = []
  for item in items:
    hrf = item.get_attribute('href')
    if hrf is None or hrf == '' or str(hrf) is None:
      continue
    if(re.match(r"https?:\/\/", str(hrf))):
      if hrf != current and host == urllib.parse.urlparse(hrf).netloc:
        result.append(hrf)
    else:
      hrf = parse.scheme + "://" + host + "/" + hrf
      result.append(hrf)
  return result


def openMyWindow(useProxy = False, isHide = True):
  opts = Options()
  opts.add_argument("user-agent=%s" % CommonFun.getUa())
  if isHide:
      opts.add_argument('--headless')
      opts.add_argument('--disable-gpu')
  if useProxy:
      opts.add_argument('--proxy-server=localhost:1080')

  driver = webdriver.Chrome(chrome_options=opts)
  driver.delete_all_cookies()
  driver.set_page_load_timeout(20)
  driver.set_script_timeout(20)
  return driver

def openMySubWindow(browser, link):
  browser.execute_script('window.open("%s");' %link)

def insertDB( proxies ):
    cnn = CommonFun.getDBConnect()
    cursor = cnn.cursor()
    values = ''
    flag = False
    for i in proxies:
      if flag:
        values = values + ','
      else:
        flag = True
      values = values + "('"+ i +"', crc32('" + i + "'))"
    sql = "insert into proxy(proxy, proxy_crc) VALUES %s ON DUPLICATE KEY UPDATE proxy=VALUES(proxy) " %values
    print(sql)
    cursor.execute( sql )
    cnn.commit()

def getProxyFromSubPage(browser, allLinks, subLinks):
  allHandles = browser.window_handles
  n = len(allHandles)
  for handle in allHandles:
      browser.switch_to_window(handle)
      result = checkHasProxy(browser)
      proxies = []
      if result:
        for i in result:
          t = re.sub(r"\s", ':', i)
          proxies.append(t)
        insertDB(proxies)
        CommonFun.saveProxy(browser.current_url)
        links = getPageAllLink(browser)
        links = list(set(links).difference(set(allLinks)))
        subLinks = list(set(subLinks).union(set(links)))
      if n > 1:
        browser.close()
        n = n - 1
  return subLinks

def subCrawler(browser, allLinks, subLinks, deep):
  print("deep: " + str(deep))
  if deep > 5:
    return 0
  allLinks = list(set(allLinks).union(set(subLinks)))
  links = []
  i = 0
  for link in subLinks:
    openMySubWindow(browser, link)
    i = i + 1
    if (i % 5 == 0)  or (i > len(subLinks) - 5):
      time.sleep(10)
      links = getProxyFromSubPage(browser, allLinks, links)
  subCrawler(browser, allLinks, links, deep + 1)




def Crawler(link):
    if CommonFun.hasProxied(link):
        print('had got it..')
        return 0
    global cnt
    global lock
    lock.acquire()
    cnt = cnt - 1
    lock.release()

    print("google: " + link)
    deep = 0
    browser = openMyWindow(True)
    subCrawler(browser, [link], [link], deep)

    lock.acquire()
    cnt = cnt + 1
    lock.release()



cnt = 5
lock=threading.Lock()

def google(keyword):
    page = 0
    while page < 5:
        print("Page: %s" %(str(page + 1)))
        driver = openMyWindow(True)
        start = str(page * 10)
        driver.get("https://www.google.com/search?q="+ keyword +"&newwindow=1&safe=strict&ei=VB55WpK9BoXwsAWN2JWQBA&start="+ start +"&sa=N&biw=1920&bih=924")
        time.sleep(4)
        itmes = driver.find_elements_by_css_selector('.mw #search .g .rc .r a')

        for item in itmes:
            hrf = item.get_attribute('href')
            while (1):
                if (cnt > 0):
                    new_thread = threading.Thread(target=Crawler, args=(hrf,))
                    new_thread.start()
                    break
                else:
                    time.sleep(2)
            time.sleep(10)
        page = page + 1



google('proxy site')
