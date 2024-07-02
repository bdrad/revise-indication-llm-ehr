from dotenv import load_dotenv
import os

load_dotenv('/mnt/sohn2022/Adrian/clinical-notes-indication-generation/models/versa/.env')

API_KEY = os.environ.get('VERSA_API_KEY')  # Match the environment variable name to the name you used in the .env file
API_VERSION = os.environ.get('VERSA_API_VERSION')
RESOURCE_ENDPOINT = os.environ.get('RESOURCE_ENDPOINT')

RETRY_SECS = 15  
MAX_RETRIES = 5

API_DETAILS = {
	"gpt4": {
		"DEPLOYMENT_ID": "gpt-4",
		"API_VERSION": "2024-05-01-preview"
	}, 
	"gpt4o": {
		"DEPLOYMENT_ID": "gpt-4o-2024-05-13",
		"API_VERSION": "2024-05-01-preview"
	}, 
	"gpt4_turbo": {
		"DEPLOYMENT_ID": "gpt-4-turbo-128k",
		"API_VERSION": "2024-05-01-preview"
	}, 
	"gpt3_5": {
		"DEPLOYMENT_ID": "gpt-35-turbo",
		"API_VERSION": "2024-05-01-preview"
	}
}