from .common_imports import *
from .config import *

# AI_FOLDER
if not os.path.exists(AI_FOLDER):
    os.makedirs(AI_FOLDER)
    os.chmod(AI_FOLDER, 0o700)

##### BKG #######################
BKG_FILE=AI_FOLDER+'bkg.txt'
DEFAULT_BKG="""
遵守以下规则：
1. 只陈述真实的内容，不猜测、不编造。
2. 不知道、不确定、没有把握的内容，直接说不知道，不要编造。
3. 不虚构人名、地名、时间、数据、论文、文献、标题、作者、来源。
4. 不夸张、不脑补、不美化。
5. 如果需要引用，只引用真实存在的内容，不编造引用。
6. 回答直接、无冗余的语气。
7. 一定要回答，不可靠也给一个最可靠的结论。
"""
if not os.path.exists(BKG_FILE):
   open(BKG_FILE,'w').write(DEFAULT_BKG)


##### TMP #######################
TMP_USE=False
TMP_SPLIT='\n_|_SPLIT_|_\n'
TMP_END='\n_|_END_|_\n'
TMP_FOLDER=AI_FOLDER+'tmp/'
try:
    import getpass
    current_user = getpass.getuser()
except Exception as e:
    try:
        current_user = os.getlogin()
    except Exception as e:
        current_user = str(os.getuid())
if not os.path.exists(TMP_FOLDER):
    os.makedirs(TMP_FOLDER)
TMP_FILE=TMP_FOLDER+DATE+'_tmp_ai_'+current_user+'.txt'
if os.path.exists(TMP_FILE):
    TMP_USE=True


###### LOG ######################
LOG_FOLDER=AI_FOLDER+'log/'
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
LOG_FILE=LOG_FOLDER+DATE+'_log_ai_'+current_user+'.txt'


###### RAG ################
RAG_SRC_VECTOR=AI_FOLDER+'vectorstore/'
RAG_SRC_DATABASE=AI_FOLDER+'database/'
if not os.path.exists(RAG_SRC_VECTOR):
    os.makedirs(RAG_SRC_VECTOR)
if not os.path.exists(RAG_SRC_DATABASE):
    os.makedirs(RAG_SRC_DATABASE)

RAG_KEYWORD_PROMPT='''
---

任务：将 <User_Message> 转化为最适合向量数据库检索的【搜索意图描述】。

规则：
1. 提取核心实体、动作和背景信息，去除寒暄和语气词。
2. 补全缩写或代词（如将“它”替换为前文提到的具体事物）。
3. 如果输入是无意义的寒暄或空话，严格仅返回 "No"。
4. 结果直接输出，禁止包含引号、多余符号或解释。
5. 长度不限，但需精准（通常 5-30 字为佳）。 
'''

RAG_CHECK_PROMPT='''
---

任务：判断 <Retrieval_Content> 中是否包含与 <Retrieval_Keywords> 相关的【事实性信息】。

规则：
1. 若【无】相关内容：严禁输出任何多余文字，只需返回单单词 "No"；
2. 若【有】相关内容：请原封不动提取相关片段（严禁改动文字），必须保留其对应的 "file_path" 和 "chunk_idx"；
3. 严禁任何解释、开头语或引号。
'''

RAG_ANSWER_PROMPT='''
---

任务：结合背景资料回答用户问题。

规则：
1. 【核心优先】：直接、准确地回答 <User_Message> 中的核心问题。
2. 【引用原则】：仅当 <References> 中的内容与问题相关时才引用。若资料无关，请忽略它们，不要强行拼凑。
3. 【能力互补】：回答应以事实为准。如果资料不全，请结合你已有的知识进行补充，但需注明哪些是补充内容。
4. 【引用标注】：如果引用了资料，请在句末标注 ["file_path" 和 "chunk_idx"]。
5. 【自我评估】：在回答最后，用一句话说明参考资料对本次回答的贡献程度（如：完全采纳/部分参考/无关未引用）。
'''




