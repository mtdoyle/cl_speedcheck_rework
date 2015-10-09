# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import pika
import os
from Queue import Queue
from threading import Thread
from datetime import datetime
import time
import re
from selenium import webdriver
from selenium.webdriver.common import keys
import MySQLdb as mdb
import sys
import random
from selenium.webdriver.common.proxy import *

state='MN'

def getUserAgent():
    user_agents=[
                    "Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20121202 Firefox/17.0 Iceweasel/17.0.1",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1 Iceweasel/15.0.1",
                    "Mozilla/5.0 (X11; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1 Iceweasel/15.0.1",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20120724 Debian Iceweasel/15.0",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0 Iceweasel/15.0",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20120721 Debian Iceweasel/15.0",
                    "Mozilla/5.0 (X11; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0 Iceweasel/15.0",
                    "Mozilla/5.0 (X11; debian; Linux x86_64; rv:15.0) Gecko/20100101 Iceweasel/15.0",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1 Iceweasel/14.0.1",
                    "Mozilla/5.0 (X11; Linux i686; rv:14.0) Gecko/20100101 Firefox/14.0.1 Iceweasel/14.0.1",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0 Iceweasel/14.0",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Debian Iceweasel/14.0",
                    "Mozilla/5.0 (X11; Linux i686; rv:14.0) Gecko/20100101 Firefox/14.0 Iceweasel/14.0",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:13.0) Gecko/20100101 Firefox/13.0.1 Iceweasel/13.0.1",
                    "Mozilla/5.0 (X11; Linux i686; rv:13.0) Gecko/20100101 Firefox/13.0.1 Iceweasel/13.0.1",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:13.0) Gecko/20100101 Firefox/13.0 Iceweasel/13.0",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:11.0a2) Gecko/20111230 Firefox/11.0a2 Iceweasel/11.0a2",
                    "Mozilla/5.0 (X11; Gentoo Linux x86_64; rv:11.0a2) Gecko/20111230 Firefox/11.0a2 Iceweasel/11.0a2",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:10.0a2) Gecko/20111118 Firefox/10.0a2 Iceweasel/10.0a2",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:10.0.7) Gecko/20100101 Firefox/10.0.7 Iceweasel/10.0.7",
                    "Mozilla/5.0 (X11; Linux ppc; rv:10.0.7) Gecko/20100101 Firefox/10.0.7 Iceweasel/10.0.7",
                    "Mozilla/5.0 (X11; Linux i686; rv:10.0.7) Gecko/20100101 Iceweasel/10.0.7",
                    "Mozilla/5.0 (X11; Linux i686; rv:10.0.7) Gecko/20100101 Firefox/10.0.7 Iceweasel/10.0.7",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:10.0.6) Gecko/20100101 Firefox/10.0.6 Iceweasel/10.0.6",
                    "Mozilla/5.0 (X11; Linux i686; rv:10.0.6) Gecko/20100101 Firefox/10.0.6 Iceweasel/10.0.6",
                    "Mozilla/5.0 (X11; Linux i686 on x86_64; rv:10.0.6) Gecko/20100101 Firefox/10.0.6 Iceweasel/10.0.6",
                    "Mozilla/5.0 (X11; Linux armv6l; rv:10.0.6) Gecko/20100101 Firefox/10.0.6 Iceweasel/10.0.6",
                    "Mozilla/5.0 (X11; Linux armv6l; rv:10.0.5) Gecko/20100101 Firefox/10.0.5 Iceweasel/10.0.5",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0 Iceweasel/10.0",
                    "Mozilla/5.0 (X11; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 Iceweasel/10.0",
        ]
    return random.choice(user_agents)


def writeToDBBadAddress(address):
    try:
        query = "insert into badaddresses " \
                "(badaddress) " \
                "values ('%s')"%(address)
        con = mdb.connect('192.168.1.114', 'clspeed', 'clspeed', 'clspeed');

        cur = con.cursor()
        cur.execute(query)
        con.commit()

    except mdb.Error, e:

        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

    finally:

        if con:
            con.close()

def writeToDB(address, speed, emm_stuff):
    street = address.split(",")[0]
    city = address.split(",")[1]
    state = address.split(",")[2]
    zip = address.split(",")[3]
    speed = speed
    emm_lat = emm_stuff[0]
    emm_lng = emm_stuff[1]
    emm_acc = emm_stuff[2]
    try:
        query = "insert into clspeed " \
                "(street,city,state,zip,speed,emm_lat,emm_lng,emm_acc) " \
                "values ('%s','%s','%s','%s',%s,%s,%s,'%s')"%(street,city,state,zip,speed,emm_lat,emm_lng,emm_acc)
        con = mdb.connect('192.168.1.114', 'clspeed', 'clspeed', 'clspeed');

        cur = con.cursor()
        cur.execute(query)
        con.commit()

    except mdb.Error, e:

        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

    finally:

        if con:
            con.close()

def test3(address, emm_stuff, sorryCycle=1):
    """

    :type sorryCycle: object
    """
    myProxy = "localhost:3128"

    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': myProxy,
        'ftpProxy': myProxy,
        'sslProxy': myProxy,
        'noProxy': '' # set this value as desired
        })
    try:
        address_orig = address
        address_tmp = address.split(',')
        address = "%s, %s, %s, %s"%(address_tmp[0],address_tmp[1],state,address_tmp[2])
        profile = webdriver.FirefoxProfile('/home/mike/.mozilla/firefox/45dghz1m.clspeed')
        user_agent = getUserAgent()
        profile.set_preference("general.useragent.override", user_agent)
        browser = webdriver.Firefox(proxy=proxy, firefox_profile=profile)
        browser.delete_all_cookies()
        browser.get('http://www.centurylink.com')
        browser.find_element_by_id('landingRes').click()
        browser.find_element_by_id('home-speed-check').click()
        browser.find_element_by_id('ctam_new-customer-link').click()
        browser.find_element_by_id('ctam_nc-sfaddress').send_keys(address)
        browser.find_element_by_css_selector('.ui-autocomplete.ui-menu.ui-widget.ui-widget-content.ui-corner-all')
        time.sleep(2)
        addressFound = browser.find_element_by_css_selector('li.ui-menu-item:nth-child(1) > a:nth-child(1)').text
        print addressFound
        browser.find_element_by_css_selector('li.ui-menu-item:nth-child(1) > a:nth-child(1)').click()
        try:
            browser.find_element_by_id('ctam_nc-go').click()
        except:
            pass

        addressFound_formatted = re.sub(r'%s (\d+)'%(state), r'%s,\1'%(state), addressFound)
        addressFound_formatted = re.sub(',USA', '', addressFound_formatted)
        count = 0
        while not 'Choose an Offer' in browser.page_source and count < 10:
            if 'We need some additional information' in browser.page_source:
                browser.find_element_by_id('addressid2').click()
                browser.find_element_by_id('submitSecUnit').click()
            time.sleep(2)
            count += 1

        try:
            # element = browser.find_element_by_css_selector('.highestSpeed')
            element = browser.find_element_by_xpath("//p[@id='highestSpeedWL']/span")
            extracted_speed_match = re.sub(',','',element.text.split(" ")[0])
        except:
            try:
                element = browser.find_element_by_xpath("//div[@id='clcoffer']/p")
                if 'CenturyLink has fiber-connected Internet with speeds up to 1 Gig in your area' in element.text:
                    writeToDBBadAddress(address_orig)
                    browser.quit()
                    return
            except:
                if browser.find_elements_by_id("mboxSorryMain").__len__() > 0:
                    browser.quit()
                    time.sleep(300)
                    sorryCycle += 1
                    if sorryCycle < 5:
                        test3(address, emm_stuff, sorryCycle)
                    else:
                        return

        # extracted_speed_match = re.search("(\d+\.?\d?)",element.text)
        #extracted_speed_match = re.search("(\d+\.?\d?)",element.text)
        if "866" not in extracted_speed_match:
            writeToDB(addressFound_formatted, extracted_speed_match, emm_stuff)
            # output = re.sub('\s+',' ', addressFound_formatted+', '+extracted_speed_match)
            # f = open(filename,'a')
            # f.write(output+",%s,%s,%s\n"%(emm_stuff[0], emm_stuff[1],emm_stuff[2]))
            # f.close()
        browser.quit()
    except:
        try:
            browser.quit()
        except:
            pass

def run_test(i):
    i = i.strip()
    emm_stuff = i.split(',')[-3:]
    test3(i, emm_stuff)

def callback(ch, method, properties, body):
    run_test('%s'%(body,))
    ch.basic_ack(delivery_tag = method.delivery_tag)

def do_stuff(q):
    while True:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='192.168.1.114'))
        channel = connection.channel()
        channel.queue_declare(queue='clspeed', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback,
                      queue='clspeed',
                      )
        channel.start_consuming()
        q.task_done()

q = Queue(maxsize=0)
num_threads = 10

for i in range(num_threads):
    worker = Thread(target=do_stuff, args=(q,))
    #worker.setDaemon(True)
    worker.start()

q.join()
