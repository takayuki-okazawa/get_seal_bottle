# -*- coding: utf-8 -*-
__author__ = 'okazawa'

import os
import sys
import logging
from packages import bottle
from packages import pyservice
import datetime
import memcache
import urllib
import urllib2

#Setting this!
DEVELOP = 1
CASH= 1

HOME = ""
STATIC_ROOT  = ""
LIST_URL2=""
RUN_HOST = ""
if DEVELOP == 1:
        #local
        HOME = "http://localhost:8080/"
        STATIC_ROOT  = "/Users/okazawa/src/get_seal_bottle/static"
        LIST_URL2="/Users/okazawa/src/get_seal_bottle/test/input.csv"
        LIST_URL3="/Users/okazawa/src/get_seal_bottle/test/input_dm.csv"
        RUN_HOST = "localhost"
else:
        #server
        HOME = "https://hoge.jp/"
        STATIC_ROOT  = "/var/www/hoge.jp/bin/static"
        LIST_URL2="/var/www/hoge/input.csv"
        LIST_URL3="/var/www/hoge/input_dm.csv"
        RUN_HOST = "127.0.0.1"

KEY1 = "URL_LIST1"
KEY2 = "URL_LIST2"
KEY3 = "URL_LIST3"
KEY_DAY = "DAY_KEY"
IMAGE_BASE1= "var objImg = document.createElement('img');var objLink = document.createElement('div');var f = new Function(\"location.href='https://trust.kyodo-d.jp/info/'\");objLink.setAttribute('onclick',\"window.open('https://trust.kyodo-d.jp/info/')\");objImg.src='"
IMAGE_BASE2= "'; objLink.appendChild(objImg);document.getElementById('"
IMAGE_BASE3= "').appendChild(objLink);"
#IMAGE_BASE1="alert('server:"
#IMAGE_BASE2="');"

#MyServer
IMAGE_S_K= HOME+"static/blue_seal_S.png"
IMAGE_M_K= HOME+"static/blue_seal_M.png"
IMAGE_L_K= HOME+"static/blue_seal_L.png"
#HostServer
IMAGE_S= HOME+"static/red_seal_S.png"
IMAGE_M= HOME+"static/red_seal_M.png"
IMAGE_L= HOME+"static/red_seal_L.png"
LIST_URL1="https://hoge/certifiedurl.txt"
USER_NAME="username"
BASIC_HOST="https://hoge"
PASSWORD="password"
CLIENT = memcache.Client(["localhost:11211"])

updateDateFlag1 = False
updateDateFlag2 = False
updateDateFlag3 = False

# monkey patching for BaseHTTPRequestHandler.log_message
def log_message(obj, format, *args):
	logging.debug("def log_message")
	logging.info("%s %s" % (obj.address_string(), format%args))

###
def cashBase(url,key):

        returnFlag = False
        day = ""
        d = ""
        global updateDateFlag1
        global updateDateFlag2
        global updateDateFlag3

        if 0==CASH:
                logging.debug("--Cash OFF--")
                if KEY1 == key:
                        updateDateFlag1 = True
                elif KEY2 == key:
                        updateDateFlag2 = True
                elif KEY3 == key:
                        updateDateFlag3 = True
                return returnFlag

	if None != CLIENT.get(key+KEY_DAY):
                day = CLIENT.get(key+KEY_DAY)
                d = getDay()
        else:
                if KEY1 == key:
                        updateDateFlag1 = True
                elif KEY2 == key:
                        updateDateFlag2 = True
                elif KEY3 == key:
                        updateDateFlag3 = True

	if day != d:
                if KEY1 == key:
                        updateDateFlag1 = True
                elif KEY2 == key:
                        updateDateFlag2 = True
                elif KEY3 == key:
                        updateDateFlag3 = True

        elif None != CLIENT.get(key):
                urlList = CLIENT.get(key)
                logging.debug("cash_"+key+"="+urlList)
                if None != urlList and -1!=urlList.find(url):
                        returnFlag = True

	return returnFlag

###
def findCash1(str):
        logging.debug("def findCash1")
        return cashBase(str,KEY1)

###
def findCash2(str):
        logging.debug("def findCash2")
        return cashBase(str,KEY2)

###
def findCash3(str):
        logging.debug("def findCash3")
        return cashBase(str,KEY3)

###
def getListBase(url,listUrl,code,key):
        logging.debug("def getListBase")
        src = ""
        returnFlag = False

        if LIST_URL1 == listUrl:
                try:
                		#Basic Auth
                        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
                        passman.add_password(None, BASIC_HOST, USER_NAME, PASSWORD)
                        authhandler = urllib2.HTTPBasicAuthHandler(passman)
                        opener = urllib2.build_opener(authhandler)
                        urllib2.install_opener(opener)
                        pagehandle = urllib2.urlopen(listUrl)
                        src = pagehandle.read()
                except Exception as e:
                        logging.debug(e)

        elif LIST_URL2 == listUrl:
                try:
                        _src = urllib.urlopen(listUrl)
                        src = _src.read()
                except Exception as e:
                        logging.debug(e)
                finally:
                        _src.close()

        elif LIST_URL3 == listUrl:
                try:
                        _src = urllib.urlopen(listUrl)
                        src = _src.read()
                except Exception as e:
                        logging.debug(e)
                finally:
                        _src.close()

        logging.debug("src= "+src)
        _url = unicode(src, code)

        CLIENT.set(key, _url)
        CLIENT.set(key+KEY3, getDay())

        if -1 != _url.find(url):
                returnFlag = True

        return returnFlag

###
def getList1(url):
    logging.debug("def getList1")
    return getListBase(url,LIST_URL1,'shift-jis',KEY1)

###
def getList2(url):
    logging.debug("def getList2")
    return getListBase(url,LIST_URL2,'utf_8',KEY2)

###
def getList3(url):
    logging.debug("def getList3")
    return getListBase(url,LIST_URL3,'utf_8',KEY3)

###
def getDay():
    logging.debug("def getDay")
    d = datetime.datetime.today()
    return str(d).split()[0]

###
def getImageURL(imageSize, SealFlag,host_name):
    logging.debug("def getImageURL")
    if imageSize == "2" and SealFlag == 1:
        return IMAGE_BASE1+IMAGE_S+IMAGE_BASE2+host_name+IMAGE_BASE3
    elif imageSize == "1" and SealFlag == 1:
        return IMAGE_BASE1+IMAGE_M+IMAGE_BASE2+host_name+IMAGE_BASE3
    elif imageSize == "0" and SealFlag == 1:
        return IMAGE_BASE1+IMAGE_L+IMAGE_BASE2+host_name+IMAGE_BASE3
    elif imageSize == "2" and SealFlag == 2:
        return IMAGE_BASE1+IMAGE_S_K+IMAGE_BASE2+host_name+IMAGE_BASE3
    elif imageSize == "1" and SealFlag == 2:
        return IMAGE_BASE1+IMAGE_M_K+IMAGE_BASE2+host_name+IMAGE_BASE3
    elif imageSize == "0" and SealFlag == 2:
        return IMAGE_BASE1+IMAGE_L_K+IMAGE_BASE2+host_name+IMAGE_BASE3
    else:
        return ""


###
@bottle.route('/getseal',method='GET',name="getseal")
def add():
        logging.debug("@bottle.route('/getseal',method='GET',name='getseal')")
        logging.debug(bottle.request.params.decode().get('dn'))
        host_name = bottle.request.params.decode().get('dn')
        imageSize = bottle.request.params.decode().get('sealid')
        seal_type = bottle.request.params.decode().get('type')
        imageURL = ""

        if "dm"==seal_type:
                if findCash3(host_name):#Find from MyServer Cash
                        logging.debug("From Cash of MyServer - Domain")
                        imageURL = getImageURL(imageSize,2,host_name)
                elif updateDateFlag3 and getList3(host_name):#Find from MyServer List
                        logging.debug("From List of MyServer - Domain")
                        imageURL = getImageURL(imageSize,2,host_name)
                return imageURL
        else:
                if findCash1(host_name):#Find from Red Cash
                        logging.debug("From Cash of Red - My page")
                        imageURL = getImageURL(imageSize,1,host_name)
                elif findCash2(host_name):#Find from MyServer Cash
                        logging.debug("From Cash of MyServer - My page")
                        imageURL = getImageURL(imageSize,2,host_name)
                elif updateDateFlag1 and getList1(host_name):#Find from Red List
                        logging.debug("From List of Red - My page")
                        imageURL = getImageURL(imageSize,1,host_name)
                elif updateDateFlag2 and getList2(host_name):#Find from MyServer List
                        logging.debug("From List of MyServer - My page")
                        imageURL = getImageURL(imageSize,2,host_name)
                return imageURL

###
@bottle.route('/static/<path:path>')
def static(path):
	logging.debug("@bottle.route('/static/<path:path>')")
	logging.info(path)
	return bottle.static_file(path,root=STATIC_ROOT)

@bottle.error(404)
def error404(error):
	logging.debug("@bottle.error(404)")
	return 'Nothing here, sorry'


# Process to run
class BottleProcess(pyservice.Process):

        pidfile = os.path.join(os.getcwd(), 'run/bottle.pid')
        logfile = os.path.join(os.getcwd(), 'log/bottle.log')

        def __init__(self):
                super(BottleProcess, self).__init__()

                from BaseHTTPServer import BaseHTTPRequestHandler
                BaseHTTPRequestHandler.log_message = log_message

        def run(self):
                logging.info('Bottle {} server starting up'.format(bottle.__version__))
                bottle.run(host='localhost', port=8080)

if __name__ == '__main__':

        if len(sys.argv) == 2 and sys.argv[1] in 'start stop restart status'.split():
                pyservice.service('getseal_background.BottleProcess', sys.argv[1])
        else:
                print 'usage: getseal_background <start,stop,restart,status>'
