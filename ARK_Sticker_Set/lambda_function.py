# -*- coding: utf-8 -*-

import requests
import time

import datetime
import sys
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import json
import telegram
from PIL import Image
from io import BytesIO
import asyncio
import re
import os
import top_holding

bot_id  = os.environ['BOT_ID']
chat_id = os.environ['CHAT_ID']
img_url = os.environ['IMG_URL']

bot = telegram.Bot(token=bot_id)


def new_sticker_set(sticker_id):
    url = 'http://seekvectorlogo.com/wp-content/uploads/2019/10/ark-invest-etfs-vector-logo.png'
    web_im = requests.get(url).content
    
    im = Image.open( BytesIO(web_im) )
    width = int(im.size[0])
    height = int(im.size[1])

    if width >= height:
        adjustHeight = int(512 / width * height)
        im_resize = im.resize((512, adjustHeight))
    else:
        adjustWidth = int(512 / height * width)
        im_resize = im.resize((adjustWidth, 512))
    
    filename = f"/tmp/{sticker_id}.png"
    im_resize.save(filename)
    
    try:
        bot.create_new_sticker_set(
            chat_id
            , f'{sticker_id}_by_Anson_bot'
            , f'{sticker_id} Trading Desk'
            , open(filename,'rb')
            , '📈'
            , timeout=20
        )
        
    except Exception as e:
        return False
    
    return True
    

async def reSize(ticker,sticker_id,act):
    # Change Foreign Ticker
    regex = r"([0-9]{4,})([A-Z]{2,})"
    matches = re.findall(regex, ticker, re.MULTILINE)
    if matches:
        if matches[0][1] == 'JP':
            # Japan to Tokyo
            ticker = matches[0][0] + '.T'
        else:
            ticker = matches[0][0] + '.'+ matches[0][1]
        
    url = f'{img_url}?ticker={ticker}&t='+str(time.time())
    web_im = requests.get(url).content

    im = Image.open( BytesIO(web_im) )
    width = int(im.size[0])
    height = int(im.size[1])

    if width >= height:
        adjustHeight = int(512 / width * height)
        im_resize = im.resize((512, adjustHeight))
    else:
        adjustWidth = int(512 / height * width)
        im_resize = im.resize((adjustWidth, 512))
    
    filename = f"/tmp/{sticker_id}{ticker}.png"
    im_resize.save(filename)
    emoji = '📈'
    if act == 'Buy':
        emoji = '📈'
    else:
        emoji = '📉'
    
    bot.add_sticker_to_set(
            chat_id
            , f'{sticker_id}_by_Anson_bot'
            , open(filename,'rb')
            , emoji
            , timeout=20
        )
    

    # print('done')
    return True


    
def main(sticker_id,ticker_list):   
    # https://github.com/Sea-n/LINE-stickers/blob/master/index.js
    asyncio.set_event_loop(asyncio.new_event_loop())
    
    tasks = []
    loop = asyncio.get_event_loop()
    task = loop.create_task(reSize(sticker_id,sticker_id,'Buy'))
    tasks.append(task)
        
    for act in ticker_list:
        # ticker = SQ
        # sticker_id = ARKF        
        # act = sell or buy
        
        for ticker in ticker_list[act]:
            task = loop.create_task(reSize(ticker,sticker_id,act))
            tasks.append(task)
    
    if tasks:
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()        
        sticker_line = f"https://t.me/addstickers/{sticker_id}_by_Anson_bot"
        
    top_holding.holding_graph(sticker_id)
    bot.add_sticker_to_set(
            chat_id
            , f'{sticker_id}_by_Anson_bot'
            , open(f'/tmp/{sticker_id}_chart.png','rb')
            , '📈'
            , timeout=20
        )

def get_old(sticker_id):
    try:
        sets = bot.get_sticker_set(name=f'{sticker_id}_by_Anson_bot')
    except Exception as e:
        return False        
    
    return sets
    

def clear_old(sticker_list):
    # Keep logo and delete others
    sticker_list = sticker_list['stickers'][1:]
    for stick in sticker_list:
        result = bot.delete_sticker_from_set(stick['file_id'])
    pass


def lambda_handler(event, context):
    sticker_id = event['sticker_id'] 
    sticker_list = event['sticker_list']
    
    if not sticker_id:
        return {'statusCode': 400}

    old_list = get_old(sticker_id)
    if not old_list:
        new_sticker_set(sticker_id)
    else:
        clear_old(old_list)

    main(sticker_id,sticker_list)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

