from .common_imports import *
from src.util import *

################################
def run():
    bkg_messages=loadBKG()
    tmp_messages=loadTMP()
    new_messages=loadNEW(sys.argv[1:])
    new_messages=checkNewMessage(new_messages)
    all_messages=bkg_messages+tmp_messages+new_messages
    result=getResult(all_messages)
    this_tmp_content=getTMP(new_messages, result)
    if(TMP_USE==True):
        writeTMP(this_tmp_content)
    if(LOG_USE==True):
        writeLOG(this_tmp_content)





