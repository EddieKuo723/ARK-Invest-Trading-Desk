import json
import matplotlib.pyplot as plt
import numpy as np
import csv
import requests
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import datetime
from decimal import Decimal
import glob
import telegram
import os

TABLE_NAME = os.environ['DYNAMODB_TABLE']
HASH_KEY   = os.environ['DYNAMODB_HASH_KEY']

dynamodb = boto3.resource(
        'dynamodb',
        region_name = 'ap-northeast-1',
    )
table = dynamodb.Table(TABLE_NAME)


def holding_graph(ark):
    response = table.get_item(
            Key={
                HASH_KEY: f'{ark}_last'
            }
        )
    
    if 'Item' in response:
        ticker_set = response['Item']['data']
    else:
        ticker_set = {}
    
    high_prices = []
    low_prices  = []
    new_price   = []
    new_tickers = []
    new_ticker_set = {}
    ark_domain = 'https://ark-funds.com/wp-content/uploads/funds-etf-csv/'
    
    ark_link = {
		"ARKK":"ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv",
		"ARKQ":"ARK_AUTONOMOUS_TECH._&_ROBOTICS_ETF_ARKQ_HOLDINGS.csv",
		"ARKW":"ARK_NEXT_GENERATION_INTERNET_ETF_ARKW_HOLDINGS.csv",
		"ARKG":"ARK_GENOMIC_REVOLUTION_ETF_ARKG_HOLDINGS.csv",
		"ARKF":"ARK_FINTECH_INNOVATION_ETF_ARKF_HOLDINGS.csv",
		"ARKX":"ARK_SPACE_EXPLORATION_&_INNOVATION_ETF_ARKX_HOLDINGS.csv"
	}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36 Edg/89.0.774.45'}

    csvdata = requests.get(f'{ark_domain}{ark_link[ark]}', headers=headers)

    open(f'/tmp/{ark}_tmp.csv', 'wb').write(csvdata.content)
    
    with open(f'/tmp/{ark}_tmp.csv', newline='') as csvfile:
        rows = csv.reader(csvfile)
        for q,row in enumerate(rows):
            if q == 0:
                # header
                continue
            elif q < 11:
                pass
                try:
                    if row[3] in ticker_set:
                        if float(row[-1][:-1]) >= float(ticker_set[row[3]]):
                            # new ratio
                            high_prices.append(float(row[-1][:-1])-float(ticker_set[row[3]]))
                            low_prices.append(0)
                            new_price.append(float(ticker_set[row[3]]))
                            new_tickers.append(row[3])
                        else:
                            high_prices.append(0)
                            low_prices.append(float(ticker_set[row[3]])-float(row[-1][:-1]))
                            new_price.append(float(row[-1][:-1]))
                            new_tickers.append(row[3])  
        
                    else:
                        high_prices.append(0)
                        low_prices.append(0)
                        new_price.append(float(row[-1][:-1]))
                        new_tickers.append(row[3])  
                except Exception as e:
                    print(e)
                
            
            if row[0] == '':
                break
            # print(row)
            new_ticker_set[row[3]] = float(row[-1][:-1])     
    
    new_ticker_set.pop('', None)
    data = json.loads(json.dumps(new_ticker_set), parse_float=Decimal)
    
    table.put_item(
            Item={
                HASH_KEY: f'{ark}_last',
                'data':data
            }
        )
    
    
    
    black = '#262626'
    blue  = '#0082fe'
    red = '#ff0000'
    green = '#3dff3d'
    orange = '#ff914c'
    pale = '#d9d9d9'
    yellow = '#fde156'
    
    plt.rcdefaults()
    fig, ax = plt.subplots()
    # to meet telegram sticker requirement
    fig.set_size_inches(5.12,3.39)
    people =tuple(new_tickers)
    y_pos = np.arange(len(people))

    
    ax.barh(y_pos, new_price, align='center',color='orange')
    ax.barh(y_pos, high_prices,left=new_price, align='center',color=green)
    
    ax.barh(y_pos, low_prices,left=new_price, align='center',color=red)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(people,fontdict={'color':'white','fontsize':15})
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_title(f'{ark} Top 10 Holdings',fontdict={'color':'white','fontsize':20})
    ax.set_facecolor(black)
    fig.set_facecolor(black)
    ax.set_frame_on(False)
    fig.tight_layout()
    pos = ax.get_position()
    point = pos.get_points()
    point[0][1] = 0
    pos.set_points(point)
    
    ax.set_position(pos)
    # plt.show()
    img = f'/tmp/{ark}_chart.png'
    plt.savefig(img, facecolor=fig.get_facecolor(), edgecolor='none')
    