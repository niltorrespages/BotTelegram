# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
import time
import requests
from geopy.distance import geodesic
from os import environ
import socket

class Station(object):

    def __init__(self, name, lat, long, dist):
        self.name = name
        self.lat = lat
        self.long = long
        self.elec = 0
        self.mech = 0
        self.distance = dist
        self.status = False

    def __str__(self):
        return(f'{self.name}: {self.lat} {self.long} a {self.distance} metres')

def fetchBicing(location):
    si = json.loads(requests.get('https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information').content)
    ss = json.loads(requests.get('https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status').content)['data'][
        'stations']
    id = 0
    stations = []
    for station in si['data']['stations']:
        stLocation = (station['lat'], station['lon'])
        dist = geodesic(location, stLocation).meters
        s = Station(station['name'], station['lat'], station['lon'], dist)
        s.status = ss[id]['status']
        s.mech = int(ss[id]['num_bikes_available_types']['mechanical'])
        s.elec = int(ss[id]['num_bikes_available_types']['ebike'])
        if s.status == 'IN_SERVICE' and s.mech + s.elec > 0:
            stations.append(s)
        id += 1
    stations.sort(key=lambda x: x.distance)
    message = []
    for i in range(0, 3):
        message.append({'text': f'{stations[i].name} amb:\nBicis elèctriques: {stations[i].elec}\nBicis mecàniques: ' \
                   f'{stations[i].mech}\nDistància: {int(stations[i].distance)} metres\n',
                        'long': stations[i].long, 'lat': stations[i].lat})
    return message

def myBicing(update, context):

    if update.message.from_user.id == MYTLGID:
        try:
            message = fetchBicing(HOME)
            for m in message:
                context.bot.sendMessage(chat_id=update.message.chat_id, text=m['text'])
                context.bot.sendLocation(chat_id=update.message.chat_id, latitude=m['lat'], longitude=m['long'])

        except Exception as e:
            context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Error al processar: {e}')
            print(e)


def specialMessage(update, context):

    if update.message.location:
        myLocation = (update.message['location']['latitude'], update.message['location']['longitude'])
        try:
            message = fetchBicing(myLocation)
            for m in message:
                context.bot.sendMessage(chat_id=update.message.chat_id, text=m['text'])
                context.bot.sendLocation(chat_id=update.message.chat_id, latitude=m['lat'], longitude=m['long'])

        except Exception as e:
            if update.message.from_user.id == MYTLGID:
                context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Error al processar: {e}')
            print(e)


'''Binance api messages'''

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

def btcPrice(update, context):
    dollars = float(json.loads(requests.get(f'{BINANCE}/api/v3/ticker/price?symbol=BTCBUSD').text)['price'])
    eur = float(json.loads(requests.get(f'{BINANCE}/api/v3/ticker/price?symbol=BTCEUR').text)['price'])
    context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Preu del bitcoin:  {dollars}$ ({eur}€)')

def ethPrice(update, context):
    dollars = float(json.loads(requests.get(f'{BINANCE}/api/v3/ticker/price?symbol=ETHBUSD').text)['price'])
    eur = float(json.loads(requests.get(f'{BINANCE}/api/v3/ticker/price?symbol=ETHEUR').text)['price'])
    context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Preu del ETH:  {dollars}$ ({eur}€)')
                                              
def adaPrice(update, context):
    dollars = float(json.loads(requests.get(f'{BINANCE}/api/v3/ticker/price?symbol=ADABUSD').text)['price'])
    eur = float(json.loads(requests.get(f'{BINANCE}/api/v3/ticker/price?symbol=ADAEUR').text)['price'])
    context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Preu del ADA:  {dollars}$ ({eur}€)')

def maticPrice(update, context):
    dollars = float(json.loads(requests.get(f'{BINANCE}/api/v3/ticker/price?symbol=MATICBUSD').text)['price'])
    eur = float(json.loads(requests.get(f'{BINANCE}/api/v3/ticker/price?symbol=MATICEUR').text)['price'])
    context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Preu del MATIC:  {dollars}$ ({eur}€)')
                                
def bitcoinWatch(context=None):
    global BTCUSD
    dollars = float(json.loads(requests.get(f'{BINANCE}/api/v3/ticker/price?symbol=BTCBUSD').text)['price'])
    eur = float(json.loads(requests.get(f'{BINANCE}/api/v3/ticker/price?symbol=BTCEUR').text)['price'])
    if BTCUSD == 0:
        BTCUSD = truncate(dollars, -3)

    elif truncate(dollars, -3) > BTCUSD:
        updater.bot.sendMessage(chat_id=MYTLGID, text=f'₿ BTC Up! {dollars}$ ({eur}€)')
        BTCUSD = truncate(dollars, -3)

    elif truncate(dollars, -3) < BTCUSD:
        updater.bot.sendMessage(chat_id=MYTLGID, text=f'₿ BTC Down! {dollars}$ ({eur}€)')
        BTCUSD = truncate(dollars, -3)
    notionUpdate(pages['BTC'], dollars)


def ethWatch(context=None):
    global ETHUSD
    dollars = float(json.loads(requests.get(f'{BINANCE}/api/v3/ticker/price?symbol=ETHBUSD').text)['price'])

    if ETHUSD == 0:
        ETHUSD = truncate(dollars, -2)

    elif truncate(dollars, -2) > ETHUSD:
        updater.bot.sendMessage(chat_id=MYTLGID, text=f'𝅉 ETH Up! {dollars}$')
        ETHUSD = truncate(dollars, -2)

    elif truncate(dollars, -2) < ETHUSD:
        updater.bot.sendMessage(chat_id=MYTLGID, text=f'𝅏 ETH Down! {dollars}$')
        ETHUSD = truncate(dollars, -2)
    notionUpdate(pages['ETH'], dollars)
                                              
def adaWatch(context=None):
    global ADAUSD
    dollars = float(json.loads(requests.get(f'{BINANCE}/api/v3/ticker/price?symbol=ADABUSD').text)['price'])

    if ADAUSD == 0:
        ADAUSD = truncate(dollars, 1)

    elif truncate(dollars, 1) > ADAUSD:
        updater.bot.sendMessage(chat_id=MYTLGID, text=f'𝅉 ADA Up! {dollars}$')
        ADAUSD = truncate(dollars, 1)

    elif truncate(dollars, 2) < ADAUSD:
        updater.bot.sendMessage(chat_id=MYTLGID, text=f'𝅏 ADA Down! {dollars}$')
        ADAUSD = truncate(dollars, 1)
    notionUpdate(pages['Ada'], dollars)

def polyWatch(context=None):
    global MATICUSD
    dollars = float(json.loads(requests.get(f'{BINANCE}/api/v3/ticker/price?symbol=MATICBUSD').text)['price'])

    if MATICUSD == 0:
        MATICUSD = truncate(dollars, 1)

    elif truncate(dollars, 1) > MATICUSD:
        updater.bot.sendMessage(chat_id=MYTLGID, text=f'𝅉 MATIC Up! {dollars}$')
        MATICUSD = truncate(dollars, 1)

    elif truncate(dollars, 2) < MATICUSD:
        updater.bot.sendMessage(chat_id=MYTLGID, text=f'𝅏 MATIC Down! {dollars}$')
        MATICUSD = truncate(dollars, 1)

    notionUpdate(pages['Matic'], dollars)

def notionUpdate(id, price):

    data = json.dumps({"properties": {"Price": price}})
    requests.patch(f"https://api.notion.com/v1/pages/{id}", headers=headers, data=data)


def notionPages():
    pages = {}
    r = requests.post("https://api.notion.com/v1/search", headers=headers)
    data = json.loads(r.text)
    for p in data['results']:
        try:
            pages.update({p["properties"]['Name']['title'][0]['plain_text']:p["id"]})
        except:
            pass
    return pages

def checkWebsite(context):
    global webUp
    try:
        code = int(requests.get(context.job.context, verify=False).status_code)
        if code != 200 and webUp:
            if dnsCheck():
                message = f'Error a {context.job.context} amb codi {code}'

            else:
                message = f'Error, resolució DNS i IP publica no son la mateixa IP'

            updater.bot.sendMessage(chat_id=MYTLGID, text=message, disable_web_page_preview=True)
            webUp = False
        elif code == 200 and not webUp:
            updater.bot.sendMessage(chat_id=MYTLGID,
                                    text=f'{context.job.context} torna a estar operativa',
                                    disable_web_page_preview=True)
            webUp = True
    except:
        if webUp:
            if dnsCheck():
                message = f'Error a {context.job.context} sense codi (TimeOut)'

            else:
                message = f'Error, resolució DNS i IP publica no son la mateixa IP'

            updater.bot.sendMessage(chat_id=MYTLGID, text=message, disable_web_page_preview=True)
            webUp = False

def dnsCheck():
    myIP = requests.get('https://checkip.amazonaws.com').text.strip()
    dnsIP = socket.getaddrinfo('niltorres.xyz', 443)[0][4]
    return dnsIP == myIP

"""Run the bot."""

### Load env and global variables


BOTTOKEN = environ['BOTTOKEN']
MYTLGID = int(environ['MYTLGID'])
HOME =(float(environ['HOMELAT']), float(environ['HOMELONG']))

# Setup Notion
NOTION = environ['NOTION']
headers = {"Notion-Version": "2022-06-28", "Authorization": f"Bearer {NOTION}", "Content-Type": "application/json"}
pages = notionPages()

BINANCE = "https://api.binance.com"

BTCUSD = 0
ETHUSD = 0
ADAUSD = 0
MATICUSD = 0


environ['TZ'] = 'Europe/Madrid'
time.tzset()

### Start bot

updater = Updater(token=BOTTOKEN, use_context=True)
jobQ = updater.job_queue

dp = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

### Handlers for commands

dp.add_handler(CommandHandler('bicing', myBicing))
dp.add_handler(CommandHandler('btc', btcPrice))
dp.add_handler(CommandHandler('eth', ethPrice))
dp.add_handler(CommandHandler('ada', adaPrice))
dp.add_handler(CommandHandler('matic', maticPrice))
dp.add_handler(MessageHandler(Filters.all, specialMessage))

### Start functions for tracking crypto

bitcoinWatch()
ethWatch()
adaWatch()
polyWatch()

### Job queues for atomatic tasks

jobQ.run_repeating(bitcoinWatch, 300)
jobQ.run_repeating(ethWatch, 300)
jobQ.run_repeating(adaWatch, 300)
jobQ.run_repeating(polyWatch, 300)

### Webiste monitor
webUp = True
jobQ.run_repeating(callback=checkWebsite, context="https://niltorres.xyz", interval=300)

### Notify new correct boot

print("Bot just booted up correctly")
updater.bot.sendMessage(chat_id=MYTLGID, text=f'Bot just booted up correctly')

updater.start_polling()
updater.idle()




