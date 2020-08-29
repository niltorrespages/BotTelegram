# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from requests import get
from datetime import datetime
import requests
from geopy.distance import geodesic
from os import environ
from dotenv import load_dotenv

load_dotenv()

WEATHERAPI = environ('WEATHERAPI')
BOTTOKEN = environ('BOTTOKEN')
MYTLGID = environ('MYTLGID')


class Station(object):

    def __init__(self, name, lat, long, dist):
        self.name = name
        self.lat = lat
        self.long = long
        self.elec = 0
        self.mech = 0
        self.distance = dist
        self.status = False


# TODO: Implement weather other than sunny or cloudy for everyday
def weather(update, context):
    temps = json.loads(get(WEATHERAPI).text)
    dia = temps["hourly"]["dt"]
    print(dia)
    print(datetime.utcfromtimestamp(dia).strftime('%Y-%m-%d %H:%M:%S'))
    message = context.bot.sendMessage(chat_id=update.message.chat_id, text='sada')


def getPublicIP(update, context):
    if update.message.from_user.id == MYTLGID:
        message = context.bot.sendMessage(chat_id=update.message.chat_id, text=get('https://api.ipify.org').text)



def specialMessage(update, context):

    # if update.message.new_chat_photo:
    #     message = context.bot.sendPoll(chat_id=update.message.chat_id, question="FoC", options=['F', 'C'], is_anonymous=False)

    if update.message.location:
        myLocation = (update.message['location']['latitude'], update.message['location']['longitude'])

        try:
            si = json.loads(requests.get('https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information').content)
            ss = json.loads(requests.get('https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status').content)['data']['stations']
            id = 0
            stations = []
            for station in si['data']['stations']:
                stLocation = (station['lat'], station['lon'])
                dist = geodesic(myLocation, stLocation)
                s = Station(station['name'],station['lat'], station['lon'],dist)
                s.status = ss[id]['status']
                s.mech = int(ss[id]['num_bikes_available_types']['mechanical'])
                s.elec = int(ss[id]['num_bikes_available_types']['ebike'])
                if s.status == 'IN_SERVICE' and s.mech + s.elec > 0:
                    stations.append(s)
                id += 1
            stations.sort(key=lambda x: x.distance)

            for i in range(0, 3):
                message = context.bot.sendMessage(chat_id=update.message.chat_id,
                                                  text=f'{stations[i].name} amb:\nBicis elèctriques:'
                                                       f' {stations[i].elec}\nBicis mecàniques: '
                                                       f'{stations[i].mech}\nDistància: {stations[i].distance}')
        except Exception as e:
            if update.message.from_user.id == MYTLGID:
                message = context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Error al processar: {e}')
            print(e)



"""Run the bot."""
updater = Updater(token=BOTTOKEN, use_context=True)

dp = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
dp.add_handler(CommandHandler('weather', weather))
dp.add_handler(CommandHandler('ip', getPublicIP))
dp.add_handler(MessageHandler(Filters.all, specialMessage))

updater.start_polling()
updater.idle()




