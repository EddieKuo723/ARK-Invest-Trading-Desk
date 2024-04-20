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
from telegram import InputSticker
from telegram.request import HTTPXRequest
from PIL import Image
from io import BytesIO
import asyncio
import re
import os
import top_holding

bot_id  = os.environ['BOT_ID']
chat_id = os.environ['CHAT_ID']
img_url = os.environ['IMG_URL']

trequest = HTTPXRequest(connection_pool_size=20)
bot = telegram.Bot(token=bot_id,request=trequest)


async def new_sticker_set(sticker_id):
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
        await bot.create_new_sticker_set(
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
    
    sticker = await bot.upload_sticker_file(
        user_id = chat_id,
        sticker = open(filename, 'rb'),
        sticker_format = "static"
    )
	sticker_dict = InputSticker(sticker.file_id,(emoji),'static' )
	await bot.add_sticker_to_set(chat_id, line_id+'_by_Anson_bot', sticker_dict)
    

    # print('done')
    return True


    
async def main(sticker_id,ticker_list):   
    # https://github.com/Sea-n/LINE-stickers/blob/master/index.js
        
    for act in ticker_list:
        # ticker = SQ
        # sticker_id = ARKF        
        # act = sell or buy
        
        for ticker in ticker_list[act]:
            await reSize(ticker,sticker_id,act)
        
    top_holding.holding_graph(sticker_id)
    filename = f'/tmp/{sticker_id}_chart.png'
	sticker = await bot.upload_sticker_file(
        user_id = chat_id, 
        sticker = open(filename, 'rb'), 
        sticker_format = "static"
    )
	sticker_dict = InputSticker(sticker.file_id,('📈'),'static' )
	await bot.add_sticker_to_set(chat_id, sticker_id+'_by_Anson_bot', sticker_dict)

async def get_old(sticker_id):
    try:
        sets = await bot.get_sticker_set(name=f'{sticker_id}_by_Anson_bot')
    except Exception as e:
        return False        
    
    return sets
    

async def clear_old(sticker_list):
    # Keep logo and delete others
    sticker_list = sticker_list['stickers'][1:]
    for stick in sticker_list:
        result = await bot.delete_sticker_from_set(stick['file_id'])
    pass

async def asyncio_main(event):
	# TODO implement
	sticker_id = event['sticker_id'] 
	sticker_list = event['sticker_list']
	
	print(json.dumps(event))
	old_list = await get_old(sticker_id)
	print(old_list)
	if not old_list:
		await new_sticker_set(sticker_id)
	else:
		print('clear')
		await clear_old(old_list)
	
	await main(sticker_id,sticker_list)

def lambda_handler(event, context):
    if 'sticker_id' not in event:
		return {'statusCode': 400}
	
	asyncio.run(asyncio_main(event))
	
	
	return {
		'statusCode': 200,
		'body': json.dumps('Hello from Lambda!')
	}

