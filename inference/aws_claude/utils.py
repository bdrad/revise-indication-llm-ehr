import os
import json
from dotenv import load_dotenv
import requests
import time

load_dotenv("/mnt/sohn2022/Adrian/Utils/Credentials/.env")

AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')  
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY') 
AWS_ENDPOINT = os.environ.get('AWS_ENDPOINT') 
AWS_REGION='us-west-2' 

from anthropic import AnthropicBedrock  # Always import AnthropicBedrock, NOT Anthropic

client = AnthropicBedrock(
    aws_access_key=AWS_ACCESS_KEY,
    aws_secret_key=AWS_SECRET_KEY,
    aws_region=AWS_REGION,
    base_url=AWS_ENDPOINT,    
)

def chat_claude3_5(prompt):
	MODEL_ID = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
	try:
		message = client.messages.create(
			max_tokens=200,
			messages=[{"role": "user", "content": prompt}],
			model=MODEL_ID
		)
		if message and hasattr(message, 'content') and len(message.content) >= 1 and len(message.content[0].text) > 0:
			return message.content[0].text
	except Exception as e:
		print(f'Error returned: {e}')