import os
from pathlib import Path
from datetime import datetime
ai_root_path = str(Path(__file__).resolve().parent.parent)+'/'
user_home_path=str(os.path.expanduser('~'))+'/'
TIMESTAMP=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
DATE=datetime.now().strftime("%Y%m%d")

##### BASIC ####################
API_URL='https://api.moonshot.cn/v1'
TEMPERATURE=0.3
MODEL_LIST=[
  'kimi-k2-thinking-turbo',
  'kimi-k2-turbo-preview',
  'kimi-k2-0905-preview',
  'kimi-k2-thinking',
  'kimi-latest',
  'moonshot-v1-auto',
  'moonshot-v1-8k',
  'moonshot-v1-32k',
  'moonshot-v1-128k'
  ]
BASIC_MODEL=MODEL_LIST[1]


##### AI FOLDER ###################
AI_FOLDER=user_home_path+'.ai/'

##### KEY #################
PROXY_URL='http://127.0.0.1:5260/v1'
REAL_KEY_FILE=AI_FOLDER+'/key.txt'
PROXY_KEY_FILE=AI_FOLDER+'/pkey.txt'


##### BKG #######################
BKG_USE=True

###### LOG ######################
LOG_USE=True

###### RAG ################
SEARCH_MODEL_PATH = '/home/toolkit/tools/ai_local_src/models/multilingual-model'
SUPPORTED_EXT=['.txt','.md']
RAG_KEYWORD_MODEL=MODEL_LIST[1]
RAG_KEYWORD_TEMPERATURE=0.2
RAG_CHECK_MODEL=MODEL_LIST[1]
RAG_CHECK_TEMPERATURE=0.0
CHUNK_SIZE=5000
CHUNK_OVERLAP=500
VECTOR_K=10





