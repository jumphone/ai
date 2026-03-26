########
# Base
import os,sys,time,json
from typing import *
from datetime import datetime
from openai import OpenAI
from openai.types.chat.chat_completion import Choice
import tty,termios,base64,httpx
