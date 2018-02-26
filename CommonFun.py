import random
import urllib
import pymysql
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import redis
import time


systerms = ['pc', 'android', 'ios', 'mac']
proxies = ['39.137.83.130:8080', '39.137.83.132:8080', '39.137.83.133:80', '39.137.83.131:8080', '121.8.98.196:80',
           '121.8.98.198:80', '121.8.98.197:80', '46.218.85.101:3129', '122.183.139.109:8080',
           '88.157.149.250:8080', '123.125.142.40:80']

def getDBConnect():
    return pymysql.connect("localhost", "root", "root", "test")

def getRedisConnect():
    pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
    return redis.Redis(connection_pool=pool)

def getRadom( min = 1, max = 0):
    if max > 0 :
        a = max - min
        return int(random.random() * a) + min
    else:
        return int(random.random() * min)

def saveProxy(link):
    cnn = getDBConnect()
    cursor = cnn.cursor()
    sql = "insert into proxy_url(link, link_crc) VALUES ('"+link+"', crc32('"+link+"')) ON DUPLICATE KEY UPDATE link=VALUES(link) "
    print(sql)
    cursor.execute(sql)
    cnn.commit()

def getProxyList(page = 0):
    cnn = getDBConnect()
    cursor = cnn.cursor()
    offset = page * 1000
    sql = "select proxy from proxy limit 1000 offset %s" %offset
    print(sql)
    cursor.execute(sql)
    return cursor.fetchall()

def hasProxied(link):
    parse = urllib.parse.urlparse(link)
    host = parse.netloc
    cnn = getDBConnect()
    cursor = cnn.cursor()
    sql = "select id from proxy_url WHERE link like '%"+host+"%' limit 1"
    cursor.execute(sql)
    info = cursor.fetchone()
    return info

def getUa(sys = 'pc'):
    index = random.random() * 2499
    cursor = getDBConnect().cursor()
    cursor.execute("select ua from ua_"+sys+" where id < " + str(index) +" order by id desc limit 1" )
    info = cursor.fetchone()
    return info[0]

def getProxy():
    index = random.random() * (len(proxies) - 1)
    proxy = proxies[int(index)]
    return proxy

def getOs(t):
    index = getRandom(len(systerms))
    return systerms[int(index)]

def getRandom(num):
    return int(random.random() * (num - 1))


def checkHasProxy(brower):
    try:
        text = brower.find_element_by_css_selector('body').text
        proxies = []
        result =re.findall(r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)[:|\s| ]+[1-9][0-9]+", text)
        if len(result) > 0:
            proxies = list(set(proxies).union(set(result)))
        result =re.findall(r"[1-9][0-9]+[ |\s]+(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", text)
        if len(result) > 0:
            proxies = list(set(proxies).union(set(result)))
        if len(proxies) > 0:
            return proxies
    except :
        pass
    return False


def openMyWindow(useProxy = False, isHide = True, timeout = 20):
    opts = Options()
    opts.add_argument("user-agent=%s" % getUa())
    if isHide:
        opts.add_argument('--headless')
        opts.add_argument('--disable-gpu')
    if useProxy:
        if str(useProxy).count(':') > 0:
            opts.add_argument('--proxy-server=%s' %str(useProxy))
        else:
            opts.add_argument('--proxy-server=localhost:1080')

    driver = webdriver.Chrome(chrome_options=opts)
    driver.delete_all_cookies()
    driver.set_page_load_timeout(timeout)
    driver.set_script_timeout(timeout)
    return driver


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


def openMySubWindow(browser, link):
    browser.execute_script('window.open("%s");' %link)

def filterProxy(pre_proxy):
    tmp = None
    result = re.findall(r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)[:|\s| ]+[1-9][0-9]+", pre_proxy)
    if len(result) > 0:
        tmp = result[0]
    result = re.findall(r"[1-9][0-9]+[ |\s]+(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", pre_proxy)
    if len(result) > 0:
        tmp = result[0]
    if tmp is None:
        return False
    t = re.sub(r"[\s|:| ]+", ':', tmp)
    arr = t.split(':', 1)
    if(len(arr[0]) > len(arr[1])):
        return arr[0] + ':' + arr[1]
    else:
        return arr[1] + ':' + arr[0]


def insertDB( proxies ):
    cnn = getDBConnect()
    cursor = cnn.cursor()
    values = ''
    flag = False
    for i in proxies:
        proxy = filterProxy(i)
        if flag:
            values = values + ','
        else:
            flag = True
        values = values + "('"+ proxy +"', crc32('" + proxy + "'))"

    sql = "insert into proxy(proxy, proxy_crc) VALUES %s ON DUPLICATE KEY UPDATE proxy=VALUES(proxy) " %values
    print(sql)
    cursor.execute( sql )
    cnn.commit()

