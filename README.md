# ARK Trading Desk
Record all purchases and sales made by [ARK Invest](https://ark-funds.com/subscribe) via [Telegram Channel](https://core.telegram.org/bots/api)

Deployed through AWS Lambda: https://t.me/ARK_Trading_Desk

## Architecture
<p align="center">
<a>
	<img src="Diagram/event_processing.png" width="300"/>
</a>

<p align="center">

## Building

1) Run `pip install -r requirements.txt` in each function folder
2) *Optional*: setup environment variable with settings:
   ```
   DYNAMODB_TABLE=******
   DYNAMODB_HASHKEY=***********
   BOT_ID=*********
   CHANNEL_ID=*********
   CHAT_ID=********
   IMG_URL=************
   ```

## Deploy

GitHub Action for deploying Lambda code to create and update function:

### Input 
See [Deploy_Get_ARK_Email.yml](/.github/workflows/Deploy_Get_ARK_Email.yml) for more detailed information.
* function-name: Get_ARK_Email

#### Github Action Secrets 
* AWS_ACCESS_KEY_ID - AWS Access Key Id
* AWS_SECRET_ACCESS_KEY - AWS Secret Key
* AWS_DEPLOY_IAM_ARN - AWS IAM Setting
* LAMBDA_VARIABLE - Lambda Functions Environment Variable

## Example
```
ARKK INNOVATION ETF
Buy
- ZM
Zoom Video Communications Inc
- SHOP
Shopify Inc
- EXAS
Exact Sciences Corp

Sell
- HUYA
Huya Inc
```

## AWS Policy

Add the following AWS policy if you want to integrate with GitHub Actions. Please change `REGION`, `ACCOUNT` and `LAMBDA_NAME` variable to your specfic data.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
         "lambda:CreateFunction",
         "lambda:UpdateFunctionCode",
         "lambda:GetFunction",
         "lambda:UpdateFunctionConfiguration",
         "iam:ListRoles",
         "iam:PassRole"
      ],
      "Resource": "arn:aws:lambda:${REGION}:${ACCOUNT}:function:${LAMBDA_NAME}"
    }
  ]
}
```

## License

This project is released under the MIT license.
For more details, take a look at the [LICENSE](LICENSE) file.