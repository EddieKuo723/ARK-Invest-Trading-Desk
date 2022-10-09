import json
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client import client, tools, file
import boto3
import base64

TABLE_NAME = os.environ['DYNAMODB_TABLE']
HASH_KEY   = os.environ['DYNAMODB_HASH_KEY']


dynamodb = boto3.resource(
        'dynamodb',
        region_name = 'ap-northeast-1',
    )
table = dynamodb.Table(TABLE_NAME)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_last_mail():
    try:
        response = table.get_item(
            Key={
                HASH_KEY: 'last_ark_mail'
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])

    try:
        last_ark_mail = response['Item']['mail_id']
    except Exception as e:
        last_ark_mail = '0'
        
    return last_ark_mail

def get_credentials():
    client_id     = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']
    refresh_token = os.environ['REFRESH_TOKEN']
    credentials = client.GoogleCredentials(None, 
    client_id, 
    client_secret,
    refresh_token,
    None,
    "https://accounts.google.com/o/oauth2/token",
    'authetication-5dbbc')

    return credentials

def lambda_handler(event, context):
    with open('/tmp/token.json', 'w') as token:
        token.write(os.environ['token_json'])

    credentials = Credentials.from_authorized_user_file('/tmp/token.json', SCOPES)

    service = build('gmail', 'v1', credentials=credentials)

    # Call the Gmail API 
    results = service.users().messages().list(userId='me',q='ark@ark-funds.com').execute()
    new = results['messages'][0]['id']
    last_mail = get_last_mail()
    if last_mail == new:
        return {
            'statusCode': 200,
            'body': json.dumps('Wait for mail~')
        }
    

    msg = service.users().messages().get(userId='me',id=new, format="full").execute()
    if msg.get("payload").get("body").get("data"):
        body = {
            'body':base64.urlsafe_b64decode(msg.get("payload").get("body").get("data").encode("ASCII")).decode("utf-8")
        }            
        
        client = boto3.client(
                'lambda',
                region_name='ap-northeast-1')
                
        response = client.invoke(
                FunctionName='ARK_Trading_Desk',
                InvocationType='Event',
                Payload= json.dumps(body)
            )
    
    response = table.put_item(
               Item={
                    HASH_KEY: 'last_ark_mail',
                    'mail_id': new
                }
            )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
