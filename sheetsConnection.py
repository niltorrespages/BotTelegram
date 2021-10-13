from __future__ import print_function
from googleapiclient.discovery import build
from google.oauth2 import service_account
from os import environ
from dotenv import load_dotenv
from pycoingecko import CoinGeckoAPI


def getSheetInfo():
    credentials = service_account.Credentials.from_service_account_file("creds.json")
    sheet_service = build('sheets', 'v4', credentials=credentials)
    id = environ['SpreadsheetId']
    range = 'Resum!B4:B12'
    data = sheet_service.spreadsheets().values().get(spreadsheetId=id, range=range).execute()
    rows = data.get('values', [])
    return rows

def setRiskInfo(risks):
    credentials = service_account.Credentials.from_service_account_file("creds.json")
    sheet_service = build('sheets', 'v4', credentials=credentials)
    id = environ['SpreadsheetId']
    valueInputOption = 'USER_ENTERED'
    range = 'Resum!G4:H12'
    body = {
        'values': risks
    }
    data = sheet_service.spreadsheets().values().update(spreadsheetId=id, range=range, body=body, valueInputOption= valueInputOption).execute()

def getAllCoinsInfo():
    credentials = service_account.Credentials.from_service_account_file("creds.json")
    sheet_service = build('sheets', 'v4', credentials=credentials)
    id = environ['SpreadsheetId']
    range = 'Resum!B4:B22'
    data = sheet_service.spreadsheets().values().get(spreadsheetId=id, range=range).execute()
    rows = data.get('values', [])
    return rows

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
    sheet_service = build('sheets', 'v4', credentials=credentials)
    id = environ['SpreadsheetId']
    valueInputOption = 'USER_ENTERED'
    range = 'Data!A1:AF50'

    body = {
        'values': info
    }
    sheet_service.spreadsheets().values().update(spreadsheetId=id, range=range, body=body, valueInputOption=valueInputOption).execute()

# def calcRiskMetric(context = None):
#     start = time.time()
#     print(f"Starting at {start}")
#     currencies = ['usd', 'btc', 'eth']
#     coins = getSheetInfo()
#     risks = {}
#     for coin in coins:
#         if coin != '':
#             for currency in currencies:
#                 if currency == 'btc' and coin == 'bitcoin':
#                     pass
#                 elif currency == 'eth' and coin == 'ethereum':
#                     pass
#                 else:
#                     df = pd.DataFrame()
#                     print(f"Calculating risk metric for {coin} in {currency}")
#                     risk = riskMetric(coinId=coin, currency=currency, df2=df)['avg'][-1]
#                     risks.update({coin:{currency:risk}})
#                     print(risks)
#     end = time.time()
#     print(f"Ending at {end}. Total time spent = {end - start}")
#     return risks
load_dotenv()
#getSheetInfo()
#calcRiskMetric()