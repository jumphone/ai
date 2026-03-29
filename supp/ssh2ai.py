
import os,time
import subprocess as sp

file_path='/home/media/my_voice_tmp.txt'
print('-'*30) 

while True:
    if os.path.exists(file_path):
        try:
            print('Message from user:')
            print()
            file_content=open(file_path,'r').read()
            print(file_content)
            os.remove(file_path)   
            print('-'*30) 
            sp.Popen(['/bin/aiw', file_content]).wait()
            print('-'*30) 
        except Exception as e:
            print("ERROR:", e)
    time.sleep(1)    


