# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import pika
import os
from Queue import Queue
from threading import Thread
from datetime import datetime
import time
import re
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
import MySQLdb as mdb
from selenium.common.exceptions import ElementNotVisibleException
import sys
import random
import glob

state = 'MN'

if len(sys.argv) > 1:
    queue_name = sys.argv[1]
else:
    queue_name = 'clspeed'

def getUserAgent():
    user_agents=[
                    "Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20121202 Firefox/17.0 Iceweasel/17.0.1",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1 Iceweasel/15.0.1",
                    "Mozilla/5.0 (X11; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1 Iceweasel/15.0.1",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0 Iceweasel/15.0",
                    "Mozilla/5.0 (X11; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0 Iceweasel/15.0",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1 Iceweasel/14.0.1",
                    "Mozilla/5.0 (X11; Linux i686; rv:14.0) Gecko/20100101 Firefox/14.0.1 Iceweasel/14.0.1",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0 Iceweasel/14.0",
                    "Mozilla/5.0 (X11; Linux i686; rv:14.0) Gecko/20100101 Firefox/14.0 Iceweasel/14.0",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:13.0) Gecko/20100101 Firefox/13.0.1 Iceweasel/13.0.1",
                    "Mozilla/5.0 (X11; Linux i686; rv:13.0) Gecko/20100101 Firefox/13.0.1 Iceweasel/13.0.1",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:13.0) Gecko/20100101 Firefox/13.0 Iceweasel/13.0",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:11.0a2) Gecko/20111230 Firefox/11.0a2 Iceweasel/11.0a2",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:10.0a2) Gecko/20111118 Firefox/10.0a2 Iceweasel/10.0a2",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:10.0.7) Gecko/20100101 Firefox/10.0.7 Iceweasel/10.0.7",
                    "Mozilla/5.0 (X11; Linux i686; rv:10.0.7) Gecko/20100101 Firefox/10.0.7 Iceweasel/10.0.7",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:10.0.6) Gecko/20100101 Firefox/10.0.6 Iceweasel/10.0.6",
                    "Mozilla/5.0 (X11; Linux i686; rv:10.0.6) Gecko/20100101 Firefox/10.0.6 Iceweasel/10.0.6",
                    "Mozilla/5.0 (X11; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 Iceweasel/10.0",
        ]
    return random.choice(user_agents)


def sorryAddressesBackToRabbit(orig):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='192.168.1.211'))
        channel = connection.channel()
        if queue_name == 'clspeedSorryAddresses':
            sorry_queue_name = 'clspeedSorryAddressesAgain'
        else:
            sorry_queue_name = 'clspeedSorryAddresses'
        channel.queue_declare(queue=sorry_queue_name, durable=True)
        channel.basic_publish(exchange='',
                    routing_key=sorry_queue_name,
                    body=orig,)
        connection.close()

def writeToDBBadAddress(address):
    try:
        query = "insert into badaddresses " \
                "(badaddress) " \
                "values ('%s')"%(address)
        con = mdb.connect(host='192.168.1.211', port='3307', user='clspeed', passwd='clspeed', db='clspeed')

        cur = con.cursor()
        cur.execute(query)
        con.commit()

    except mdb.Error, e:

        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

    finally:

        if con:
            con.close()

def createDB():
    charset = "CHARACTER SET utf8 COLLATE utf8_general_ci"

    query = "create table if not exists clspeed " \
            "(street varchar(100) {0}, city varchar(100) {0}, state varchar(2) {0}, zip int(5), speed decimal(5,1), " \
            "emm_lat decimal(12,10), emm_lng decimal(12,10), emm_acc varchar(20) {0})".format(charset)

    con = mdb.connect(host='192.168.1.211', port=3307, user='clspeed', passwd='clspeed', db='clspeed')

    cur = con.cursor()
    cur.execute(query)
    con.commit()


def writeToDB(address, speed, emm_stuff):
    street = address.split(",")[0]
    city = address.split(",")[1]
    state = address.split(",")[2]
    zip = address.split(",")[3]
    speed = speed
    emm_lat = emm_stuff[0]
    emm_lng = emm_stuff[1]
    emm_acc = emm_stuff[2]
    con = None

    charset = "CHARACTER SET utf8 COLLATE utf8_general_ci"

    query = "create table if not exists clspeed " \
            "(street varchar(100) {0}, city varchar(100) {0}, state varchar(2) {0}, zip int(5), " \
            "emm_lat decimal(12,10), emm_lng decimal(12,10), emm_acc varchar(20) {0})".format(charset)

    try:
        query = "insert into clspeed " \
                "(street,city,state,zip,speed,emm_lat,emm_lng,emm_acc) " \
                "values ('%s','%s','%s','%s',%s,%s,%s,'%s')"%(street,city,state,zip,speed,emm_lat,emm_lng,emm_acc)
        con = mdb.connect(host='192.168.1.211', port=3307, user='clspeed', passwd='clspeed', db='clspeed')

        cur = con.cursor()
        cur.execute(query)
        con.commit()

    except mdb.Error, e:

        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

    finally:

        if con:
            con.close()

def test3(address, emm_stuff):
    # try:
    address_orig = address
    address_tmp = address.split(',')
    address = "%s, %s, %s"%(address_tmp[0],address_tmp[1],address_tmp[2])
    # firefox_binary = FirefoxBinary("/Applications/firefox_41/Firefox.app/Contents/MacOS/firefox")
    # browser = webdriver.Firefox(firefox_binary=firefox_binary)
    browser = webdriver.Firefox()
    browser.set_window_size(1000,1000)
    browser.delete_all_cookies()
    browser.get('http://www.centurylink.com/home/internet/')
    browser.find_element_by_id('btnInternetTabOnly').click()
    # browser.find_element_by_id('home-speed-check').click()
    browser.find_element_by_id('ctam_nc-sfaddress').click()
    browser.find_element_by_id('ctam_nc-sfaddress').send_keys(address)
    time.sleep(1)

    if browser.find_elements_by_class_name("ui-menu-item").__len__() > 0:
        addressFound = browser.find_elements_by_class_name("ui-menu-item")[0].text
        browser.find_elements_by_class_name("ui-menu-item")[0].click()
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
        if browser.find_elements_by_id('noMatch').__len__() > 0:
            browser.quit()
            return
        time.sleep(2)
        count += 1

    extracted_speed_match = None
    # element = browser.find_element_by_css_selector('.highestSpeed')
    if browser.find_elements_by_xpath("//p[@id='highestSpeedWL']/span").__len__()>0:
        element = browser.find_element_by_xpath("//p[@id='highestSpeedWL']/span")
        extracted_speed_match = re.sub(',','',element.text.split(" ")[0])
    elif browser.find_elements_by_xpath("//div[@id='clcoffer']/p").__len__()>0:
        element = browser.find_element_by_xpath("//div[@id='clcoffer']/p")
        if 'CenturyLink has fiber-connected Internet with speeds up to 1 Gig in your area' in element.text:
            writeToDBBadAddress(address_orig)
            browser.quit()
            return
    elif browser.find_elements_by_id("mboxSorryMain").__len__() > 0:
            sorryAddressesBackToRabbit(address_orig)
            browser.quit()
            if queue_name == 'clspeed':
                time.sleep(600)
            return
    elif browser.find_elements_by_id("mainoffer").__len__() > 0:
        element = browser.find_element_by_xpath("//div[@id='mainoffer']/p")
        if 'We are temporarily experiencing system issues' in element.text:
            writeToDBBadAddress(address_orig)
            browser.quit()
            return
    elif browser.find_elements_by_xpath("//div[@id='internet_highest_speed_wrap']/div").__len__()>0:
        if (browser.find_element_by_xpath("//div[@id='internet_highest_speed_wrap']/div").get_attribute("class")) == "internet_dialup_wrap":
            writeToDBBadAddress(address_orig)
            browser.quit()
            return

    if extracted_speed_match:
        if "866" not in extracted_speed_match:
            writeToDB(addressFound_formatted, extracted_speed_match, emm_stuff)
            browser.quit()
            return
        else:
            print "Error with address {0}".format(address)
            return

    # except:
    #     try:
    #         browser.quit()
    #         writeToDBBadAddress(address_orig)
    #     except:
    #         pass


def run_test(i):
    i = i.strip()
    emm_stuff = i.split(',')[-3:]
    createDB()
    test3(i, emm_stuff)

def callback(ch, method, properties, body):
    run_test('%s'%(body,))
    ch.basic_ack(delivery_tag = method.delivery_tag)

def do_stuff(q):
    while True:
        credentials = pika.PlainCredentials('guest', 'guest')

        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='192.168.1.211', port=5673, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback,
                      queue=queue_name,
                      )
        channel.start_consuming()
        q.task_done()

q = Queue(maxsize=0)
num_threads = 5



for i in range(num_threads):
    worker = Thread(target=do_stuff, args=(q,))
    #worker.setDaemon(True)
    worker.start()

q.join()
