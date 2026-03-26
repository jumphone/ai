from .safe import *

##### CLIENT ####################

REAL_KEY_FILE_FLAG=True
while True:
    if os.path.exists(REAL_KEY_FILE) and REAL_KEY_FILE_FLAG:
        PASSWD=open(REAL_KEY_FILE).readline().rstrip()
    else:
        PASSWD=getpass_star('ai-key: ')
        if PASSWD=='q':
            exit()
    API_KEY=PASSWD
    #print(API_KEY)
    if fast_verify_key(API_KEY, API_URL):
        #print('KEY和真实地址验证通过')
        client = OpenAI(api_key=API_KEY,base_url=API_URL,)
        if not os.path.exists(REAL_KEY_FILE) or not REAL_KEY_FILE_FLAG:
            open(REAL_KEY_FILE,'w').write(PASSWD)
        break
    else:
        if fast_verify_key(API_KEY, PROXY_URL):
            #print('KEY和代理地址验证通过')
            client = OpenAI(api_key=API_KEY,base_url=PROXY_URL,)
            if not os.path.exists(PROXY_KEY_FILE) or not REAL_KEY_FILE_FLAG:
                open(PROXY_KEY_FILE,'w').write(PASSWD)
            break
        else:
            #print('KEY和真实及代理都没通过')
            print("please input the correct key! (input 'q' to quit.)")
            REAL_KEY_FILE_FLAG=False
