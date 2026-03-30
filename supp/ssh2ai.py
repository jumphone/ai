
import os,time
import subprocess as sp
from datetime import datetime

DASH_LINE='-'*50

file_dir='/home/media/voice_dir/'
print(DASH_LINE) 

def get_timestamp():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output='['+str(timestamp)+'] '
    return(output)

def print_ts(text):
    output=get_timestamp()+text
    print(output)

while True:
    file_list= os.listdir(file_dir)
    if len(file_list)>0:
        for file_name in file_list:
            print(file_name)
            print(DASH_LINE)
            file_path=os.path.join(file_dir, file_name)
            try:
                print_ts('Message:')
                print()
                file_content=open(file_path,'r').read()
                print(file_content)
                os.remove(file_path)   
                print(DASH_LINE)
                print_ts('Result:') 
                print()
                sp.Popen(['/home/media/ai/bin/aiw.py', file_content]).wait()
                print()
                print(DASH_LINE) 
            except Exception as e:
                print("ERROR:", e)
    time.sleep(1)    


