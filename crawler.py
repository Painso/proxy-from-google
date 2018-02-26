import time
import re
import threading
import urllib
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import CommonFun


class Crawler:
    def idcloak(self):
        url = 'http://www.idcloak.com/proxylist/proxy-list.html'
        browser = CommonFun.openMyWindow(True, True, 100)
        browser.get(url)
        time.sleep(5)
        i = 2
        while i < 11:
            proxies = CommonFun.checkHasProxy(browser)
            if proxies:
                CommonFun.insertDB(proxies)
            items = browser.find_elements_by_css_selector('.pagination input')
            for item in items:
                if item.get_attribute('value') == str(i):
                    try:
                        item.click()
                    except:
                        try:
                            item.send_keys(Keys.SPACE)
                        except:
                            pass
                    break
            time.sleep(5)
            i = i + 1

    def live_socks(self):
        url = 'http://www.live-socks.net/search?max-results=15'
        browser = CommonFun.openMyWindow(True, True, 100)
        browser.get(url)
        time.sleep(10)
        items = browser.find_elements_by_css_selector('.entry-title a')
        for item in items:
            CommonFun.openMySubWindow(browser, item.get_attribute('href'))
            time.sleep(2)
        time.sleep(5)
        allHandles = browser.window_handles
        for handle in allHandles:
            browser.switch_to_window(handle)
            proxies = CommonFun.checkHasProxy(browser)
            if proxies:
                CommonFun.insertDB(proxies)
            browser.close()

    def socks24(self):
        url = 'http://www.socks24.org/search?max-results=15'
        browser = CommonFun.openMyWindow(True, True, 100)
        browser.get(url)
        time.sleep(10)
        items = browser.find_elements_by_css_selector('.entry-title a')
        for item in items:
            CommonFun.openMySubWindow(browser, item.get_attribute('href'))
            time.sleep(2)
        time.sleep(5)
        allHandles = browser.window_handles
        for handle in allHandles:
            browser.switch_to_window(handle)
            proxies = CommonFun.checkHasProxy(browser)
            if proxies:
                CommonFun.insertDB(proxies)
            browser.close()


    def local(self):
        i = 0
        browser = CommonFun.openMyWindow(False, True, 3)
        url = 'file:///C:/Users/Pains/Desktop/vipsocks.txt'
        while i < 3:
            browser.get(url)
            time.sleep(1)
            proxies = CommonFun.checkHasProxy(browser)
            if proxies:
                CommonFun.insertDB(proxies)
            i = i + 1
            url = "file:///C:/Users/Pains/Desktop/vipsocks (%s).txt" %i
            break
        browser.close()

    def spys(self):
        browser = CommonFun.openMyWindow(True, True, 100)
        urls = ['http://spys.one/en/free-proxy-list/','http://spys.one/free-proxy-list/US/', 'http://spys.one/en/anonymous-proxy-list/','http://spys.one/en/https-ssl-proxy/', 'http://spys.one/en/socks-proxy-list/', 'http://spys.one/en/http-proxy-list/', 'http://spys.one/en/non-anonymous-proxy-list/']
        for url in urls:
            browser.get(url)
            time.sleep(5)
            try:
                Select(browser.find_element_by_id('xpp')).select_by_index(5)
                time.sleep(4)
                proxies = CommonFun.checkHasProxy(browser)
                if proxies:
                    CommonFun.insertDB(proxies)
            except:
                pass

    def proxylistplus(self):
        i = 1
        browser = CommonFun.openMyWindow(True, True, 30)
        while i <= 6:
            url = "https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-%s" %i
            browser.get(url)
            time.sleep(5)
            proxies = CommonFun.checkHasProxy(browser)
            if proxies:
                CommonFun.insertDB(proxies)
            i = i + 1
        browser.close()

    def premproxy(self):
        i = 1
        browser = CommonFun.openMyWindow(True, True, 30)
        while i <= 19:
            url = "https://premproxy.com/socks-list/%s.htm" %i
            browser.get(url)
            time.sleep(10)
            proxies = CommonFun.checkHasProxy(browser)
            if proxies:
                CommonFun.insertDB(proxies)
            i = i + 1
        browser.close()


crawler = Crawler()

crawler.idcloak()
crawler.live_socks()
# crawler.socks24()
# crawler.local()

#crawler.spys()
# crawler.proxylistplus()
# crawler.premproxy()
