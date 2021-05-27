import json
import base64
import boto3
from bs4 import BeautifulSoup
from telegram.ext import Updater
from telegram import InlineKeyboardButton,InlineKeyboardMarkup
import telegram
import os


def handle(text):
    soup = BeautifulSoup(text,'html.parser')
    header = True
    sellbuy = []
    
    for tag in soup.find_all('tr'):
        if header:
            header = False
            continue
    
        item = []
        for td in tag.find_all('td'):
            item.append(td.getText())
            
        if len(item) < 9:
            continue
        sellbuy.append(item)
    
    output = {}    
    name_set = {}
    sticker = []
    batch_list = []
    
    # move[1]: ARK ETF NAME
    # move[3]: SELL OR BUY
    # move[4]: Symbol (eg. AAPL)
    # move[5]: CUSIP
    # move[6]: Company Name
    for move in sellbuy:
        us_ticker = move[4].replace('.US','',1)
        if move[1] not in output:
            output[move[1]] = {}
            
        if move[3] not in output[move[1]]:
            output[move[1]][move[3]] = [us_ticker]
        else:
            output[move[1]][move[3]].append(us_ticker)
        
        sub = move[6].replace('\n',' ')
        name_set[us_ticker] = sub.title()
        
        if us_ticker not in sticker:
            sticker.append(us_ticker)
        
    
    return output,name_set
    
def make_sticker(sticker):
    # invoke lambda
    for  sticker_id,sticker_list in sticker.items():
        data = {}
        data['sticker_id'] = sticker_id
        data['sticker_list'] = sticker_list
        json_data = json.dumps(data)
        client = boto3.client(
            'lambda',
            region_name='ap-northeast-1')
        response = client.invoke(
            FunctionName='ARK_Sticker_Set',
            InvocationType='Event',
            Payload= json_data
        )
    pass
    
def send_message(sticker,name_set):
    channel_id = os.environ['CHANNEL_ID']
    bot_id = os.environ['BOT_ID']
    bot = telegram.Bot(token=bot_id)
    ark_dict = {
        'ARKK':'INNOVATION ETF',
        'ARKQ':'Autonomous Technology & Robotics ETF',
        'ARKW':'Next Generation Internet ETF',
        'ARKG':'Genomic Revolution ETF',
        'ARKF':'FINTECH INNOVATION ETF',
        'ARKX':'Space Exploration ETF'
    }
    
    for ARK in sticker:
        etf_name = ''
        if ARK in ark_dict:
            etf_name = ark_dict[ARK]
        
        message = f"<a href='tg://addstickers?set={ARK}_by_Anson_bot'>{ARK} {etf_name}</a>"
        
        for action in sticker[ARK]:
            # Sell or Buy
            message += '\n'
            message += f'<b>{action}</b>\n'
            for ticker in sticker[ARK][action]:
                name = name_set[ticker]
                message += f"- <code>{ticker}</code>\n{name}\n"
        message += '\n'
        bot.send_message(chat_id=channel_id, text=message,disable_notification=True, parse_mode='HTML')
        


def lambda_handler(event, context):

    if 'body' in event:
        output,name_set = handle(event['body'])
        
        # make sticker set
        make_sticker(output)
        
        # send message to Channel
        send_message(output,name_set)
        
        
    return {
        'statusCode': 200,
        'body': json.dumps('Done')
    }
