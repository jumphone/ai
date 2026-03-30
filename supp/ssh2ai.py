
import os,time
import subprocess as sp
from datetime import datetime

file_path='/home/media/my_voice_tmp.txt'
print('-'*30) 


def get_timestamp():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output='['+str(timestamp)+'] '
    return(output)

def print_ts(text):
    output=get_timestamp()+text
    print(output)

while True:
    if os.path.exists(file_path):
        try:
            print_ts('Message:')
            print()
            file_content=open(file_path,'r').read()
            print(file_content)
            os.remove(file_path)   
            print('-'*30)
            print_ts('Result:') 
            print()
            sp.Popen(['/bin/ai', file_content]).wait()
            print()
            print('-'*30) 
        except Exception as e:
            print("ERROR:", e)
    time.sleep(1)    


