from __future__ import print_function
from googleapiclient.discovery import build
from google.oauth2 import service_account
from os import environ
from pycoingecko import CoinGeckoAPI
from datetime import date


def getSheetInfo():
    credentials = service_account.Credentials.from_service_account_file("creds.json")
    sheet_service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
    id = environ['SpreadsheetId']
    range = 'Resum!B4:B12'
    data = sheet_service.spreadsheets().values().get(spreadsheetId=id, range=range).execute()
    rows = data.get('values', [])
    return rows

def setRiskInfo(risks):
    credentials = service_account.Credentials.from_service_account_file("creds.json")
    sheet_service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
    id = environ['SpreadsheetId']
    valueInputOption = 'USER_ENTERED'
    range = f'Resum!H4:I{len(risks)+4}'
    body = {
        'values': risks
    }
    data = sheet_service.spreadsheets().values().update(spreadsheetId=id, range=range, body=body, valueInputOption= valueInputOption).execute()

def getTokensInfo(num):
    credentials = service_account.Credentials.from_service_account_file("creds.json")
    sheet_service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
    id = environ['SpreadsheetId']
    range = f'Resum!C4:C{num+4}'
    data = sheet_service.spreadsheets().values().get(spreadsheetId=id, range=range).execute()
    rows = data.get('values', [])
    return rows

def getAllCoinsInfo():
    credentials = service_account.Credentials.from_service_account_file("creds.json")
    sheet_service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
    id = environ['SpreadsheetId']
    range = 'Resum!B4:B22'
    data = sheet_service.spreadsheets().values().get(spreadsheetId=id, range=range).execute()
    rows = data.get('values', [])
    return rows

def setHistoryData():
    credentials = service_account.Credentials.from_service_account_file("creds.json")
    sheet_service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
    id = environ['SpreadsheetId']
    range = 'Resum!A:O'
    data = sheet_service.spreadsheets().values().get(spreadsheetId=id, range=range).execute()
    rows = data.get('values', [])
    lastData = 0
    for i, row in enumerate(reversed(rows)):
        if row and row[0] == "Sold":
            lastData = len(rows) - 1 - i
    data = rows[:lastData]
    badList = ['', 'Main Coins', 'Secondary Coins', 'Shit Coins', 'Stable coins', 'NFT', 'Active']
    today = date.today()
    newData = []
    for j, row in enumerate(data):
        if row and row[0] and row[0] not in badList:
            newData.append([])
            price = float(row[13].replace('$','').replace('.','').replace(',','.'))
            coin = float(row[14].replace('$','').replace('.','').replace(',','.'))
            now = today.strftime("%d/%m/%Y")
            newData[len(newData) - 1].append(now + " " + row[0])
            newData[len(newData) - 1].append(now)
            newData[len(newData) - 1].append(row[0])
            newData[len(newData) - 1].append(price)
            newData[len(newData) - 1].append(coin)
            newData[len(newData) - 1].append(coin * price)
    newRange = 'History!B:F'
    body = {
        'values': newData
    }
    valueInputOption = 'USER_ENTERED'
    sheet_service.spreadsheets().values().append(spreadsheetId=id, range=newRange, body=body, valueInputOption=valueInputOption).execute()

def setCoinsInfo():
    cg = CoinGeckoAPI()
    coins = getAllCoinsInfo()
    c = ""
    for coin in coins:
        if len(coin) == 0:
            i = ""
        else:
            i = coin[0]
        c += ","
        c += i
    cginfo = cg.get_coins_markets(vs_currency='usd', ids=c, price_change_percentage='1h,24h,7d')

    info = []
    info.append(list(cginfo[0].keys()))
    for i, values in enumerate(cginfo):
        values['roi'] = ''
        info.append(list(cginfo[i].values()))
    credentials = service_account.Credentials.from_service_account_file("creds.json")
    sheet_service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
    id = environ['SpreadsheetId']
    valueInputOption = 'USER_ENTERED'
    range = 'Data!A1:AF50'

    body = {
        'values': info
    }
    sheet_service.spreadsheets().values().update(spreadsheetId=id, range=range, body=body, valueInputOption=valueInputOption).execute()
