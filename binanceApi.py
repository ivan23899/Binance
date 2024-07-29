import requests
import json
import time
from datetime import datetime
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def get_p2p_prices(asset='USDT', fiat='BOB', trade_type='BUY', rows=10, page=1):
    url = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    payload = {
        "asset": asset,
        "fiat": fiat,
        "merchantCheck": False,
        "page": page,
        "payTypes": [],
        "publisherType": None,
        "rows": rows,
        "tradeType": trade_type
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['data'], len(data['data']) == rows
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos P2P: {e}")
        return [], False

def save_to_json(data, filename='p2p_prices.json'):
    try:
        with open(filename, 'a') as jsonfile:
            for offer in data:
                json.dump(offer, jsonfile, indent=4)
                jsonfile.write('\n')
        print(f"Datos guardados en el archivo JSON: {filename}")
    except IOError as e:
        print(f"Error al escribir en el archivo JSON: {e}")

def mongo_atlas_insert(data, table_name):
    uri = "mongodb+srv://clarosfernandezruddyivan:dYihYZ4mB59IAvJD@cluster0.pa9jm6b.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        db = client['binancedb']
        collection = db[table_name]
        for offer in data:
            if collection.find_one({"advNo":offer.get('adv',{}).get('advNo')}) is None:
                adv = {
                    "advNo": offer.get('adv',{}).get('advNo'),
                    "date": datetime.now(),
                    "classify": offer.get('adv',{}).get('classify'),
                    "tradeType": offer.get('adv',{}).get('tradeType'),
                    "fiatUnit": offer.get('adv',{}).get('fiatUnit'),
                    "price": offer.get('adv',{}).get('price'),
                    "surplusAmount": offer.get('adv',{}).get('surplusAmount'),
                    "tradableQuantity": offer.get('adv',{}).get('tradableQuantity'),
                    "maxSingleTransAmount": offer.get('adv',{}).get('maxSingleTransAmount'),
                    "minSingleTransAmount": offer.get('adv',{}).get('minSingleTransAmount'),
                    "tradeMethods": offer.get('adv',{}).get('tradeMethods'),
                    "isSafePayment": offer.get('adv',{}).get('isSafePayment'),
                    "advertiser": offer.get('advertiser'),
                }
                collection.insert_one(adv)
                adv.clear()
            else:
                print(f"El documento con el advNo {offer.get('adv',{}).get('advNo')} ya existe.")
        client.close()
    except Exception as e:
        print(e)

def main():
    asset = 'USDT'
    fiat = 'BOB'
    trade_type_sell = 'SELL'
    trade_type_buy = 'BUY'
    table_name_sell = 'pricep2psell'
    table_name_buy = 'pricep2pbuy'
    rows_per_page = 10
    page = 1
    #Sell
    while True:
        p2p_data, has_more = get_p2p_prices(asset, fiat, trade_type_sell, rows_per_page, page)
        mongo_atlas_insert(p2p_data, table_name_sell)
        if not p2p_data:
            break
        if not has_more:
            break
        page += 1
        time.sleep(1)  
    #Buy
    while True:
        p2p_data, has_more = get_p2p_prices(asset, fiat, trade_type_buy, rows_per_page, page)
        mongo_atlas_insert(p2p_data, table_name_buy)
        if not p2p_data:
            break
        if not has_more:
            break
        page += 1
        time.sleep(1)  


if __name__ == "__main__":
    main()