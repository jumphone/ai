from .rag import *
from .check import *


def loadBKG():
    bkg_messages=[]
    if(BKG_USE==True):
        bkg_content=open(BKG_FILE, 'r', encoding='utf-8', errors='ignore').read()
        bkg_messages.append({'role':'system','content':bkg_content})
        bkg_messages.append({'role':'system','content':'现在的准确日期和时间是:'+TIMESTAMP})
    return(bkg_messages)

def loadTMP():
    #load chat histroy
    tmp_messages=[]
    if(TMP_USE==True):
        if os.path.isfile(TMP_FILE):
            all_tmp=open(TMP_FILE, 'r', encoding='utf-8', errors='ignore').read()
            all_tmp_lines=all_tmp.rstrip().split(TMP_END)
            for line in all_tmp_lines:
                try:
                    this_content_seq=line.rstrip().split(TMP_SPLIT)
                    this_user={'role':'user','content':this_content_seq[-2]}
                    this_assistant={'role':'assistant','content':this_content_seq[-1]}
                    tmp_messages.append(this_user)
                    tmp_messages.append(this_assistant)
                except Exception as e:
                    pass
    return(tmp_messages)


def loadNEW(ARGV):
    new_argv=ARGV
    new_content_list=[]
    for this_content in new_argv:
        if os.path.isfile(this_content):
            file_content=open(this_content, 'r', encoding='utf-8', errors='ignore').read()
            new_content_list.append("Here is a file named '"+this_content+"'. File content:")
            new_content_list.append(file_content)
            new_content_list.append("# File content of '"+this_content+"' ended.")
        else:
            new_content_list.append(this_content)
    new_content=' '.join(new_content_list)
    #############################################
    new_messages=[{"role":"user","content":new_content}]
    return(new_messages)


def writeTMP(this_tmp_content):
    try:
        with open(TMP_FILE, 'a+', encoding='utf-8') as file:
            file.write(this_tmp_content+'\n')
        os.chmod(TMP_FILE, 0o777)
    except Exception as e:
        print("Attention: can't write '"+TMP_FILE+"'.")
        pass

def writeLOG(this_tmp_content):
    try:
        with open(LOG_FILE, 'a+', encoding='utf-8') as file:
            file.write(this_tmp_content+'\n')
        os.chmod(LOG_FILE, 0o777)
    except Exception as e:
        print("Attention: can't write '"+LOG_FILE+"'.")
        pass


def print_cn_all(text):
    #modified print function to solve encoding problems
    out_text=text
    sys.stdout.buffer.write(out_text.encode('utf-8'))

def print_cn(text, chunk_size=5, delay=0.05):
    #modified print function to solve encoding problems
    #out_text=text
    #sys.stdout.buffer.write(out_text.encode('utf-8'))
    import sys
    import time
    for i in range(0, len(text), chunk_size):
        out_text = text[i:i + chunk_size]
        sys.stdout.buffer.write(out_text.encode('utf-8'))
        sys.stdout.buffer.flush()  # 立即输出，避免缓冲
        time.sleep(delay)  # 模拟流式输出的延迟
    sys.stdout.buffer.flush()


def cleanContent(text):
    #remove '\n' and split_tag in content
    #out_text=text.replace('\n',' ').replace(TMP_SPLIT,' ')
    out_text=text.replace(TMP_SPLIT,' ').replace(TMP_END,' ')
    return(out_text)

def checkNewMessage(new_messages):
    new_content=new_messages[0]['content']
    if(new_content.rstrip() in ['stoptmp','rmtmp']):
        if os.path.exists(TMP_FILE):
            # 删除TMP文件
            os.remove(TMP_FILE)
        print("'"+TMP_FILE+"' has been removed.")
        exit()
    if(new_content.rstrip() in ['usetmp','tmp']):
        with open(TMP_FILE, 'a+', encoding='utf-8') as file:
            file.write('\n')
        print("'"+TMP_FILE+"' has been created.")
        os.chmod(TMP_FILE, 0o777)
        exit()
    if(new_content.rstrip()=='cleantmp'):
        if os.path.exists(TMP_FILE):
            # 删除TMP文件
            os.remove(TMP_FILE)
        print("'"+TMP_FILE+"' has been removed.")
        with open(TMP_FILE, 'a+', encoding='utf-8') as file:
            file.write('\n')
        print("'"+TMP_FILE+"' has been created.")
        os.chmod(TMP_FILE, 0o777)
        exit()
    #############################################
    if(new_content.rstrip()==''):
        print('Error, message is empty!')
        exit()
    return(new_messages)


def getTMP(new_messages, result):
    new_content=new_messages[0]['content']
    current_timestamp = TIMESTAMP
    current_path = os.getcwd()
    current_model = BASIC_MODEL
    script_path = os.path.abspath(sys.argv[0])
    tmp_content=TMP_SPLIT.join([current_timestamp, current_path, current_user,
                                script_path, current_model,
                                cleanContent(new_content), cleanContent(result)])
    tmp_content=tmp_content+TMP_END
    return(tmp_content)


def getResult(messages, verbose=True):
    stream = client.chat.completions.create(
        model = BASIC_MODEL,
        messages = messages,
        temperature = TEMPERATURE,
        stream=True, 
        )
    result=''
    for chunk in stream:
        delta = chunk.choices[0].delta 
        if delta.content:
            if verbose:
                print_cn(delta.content)
            else:
                print_cn_all(delta.content)
            result=result+delta.content
    print('')
    return(result)



def search_impl(arguments: Dict[str, Any]) -> Any:
    """
    在使用 Moonshot AI 提供的 search 工具的场合，只需要原封不动返回 arguments 即可，
    不需要额外的处理逻辑。
 
    但如果你想使用其他模型，并保留联网搜索的功能，那你只需要修改这里的实现（例如调用搜索
    和获取网页内容等），函数签名不变，依然是 work 的。
 
    这最大程度保证了兼容性，允许你在不同的模型间切换，并且不需要对代码有破坏性的修改。
    """
    return arguments



from contextlib import contextmanager

@contextmanager
def silence_stderr():
    # 将标准错误流重定向到空设备
    new_target = open(os.devnull, 'w')
    old_stderr = sys.stderr
    sys.stderr = new_target
    try:
        yield
    finally:
        sys.stderr = old_stderr
        new_target.close()

def chat(messages) -> Choice:
    with silence_stderr():
        completion = client.chat.completions.create(
            model=BASIC_MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            tools=[
                {
                    "type": "builtin_function",  # <-- 使用 builtin_function 声明 $web_search 函数，请在每次请求都完整地带上 tools 声明
                    "function": {
                        "name": "$web_search",
                    },
                }
            ]
        )
    return completion.choices[0]



def getResult_web(messages, verbose=True):
    if verbose:
        print_cn("WEB | checking ...\n")
    finish_reason = None
    while finish_reason is None or finish_reason == "tool_calls":
        choice = chat(messages)
        finish_reason = choice.finish_reason
        if finish_reason == "tool_calls":  # <-- 判断当前返回内容是否包含 tool_calls
            messages.append(choice.message)  # <-- 我们将 Kimi 大模型返回给我们的 assistant 消息也添加到上下文中，以便于下次请求时 Kimi 大模型能理解我们>的诉求
            for tool_call in choice.message.tool_calls:  # <-- tool_calls 可能是多个，因此我们使用循环逐个执行
                tool_call_name = tool_call.function.name
                tool_call_arguments = json.loads(tool_call.function.arguments)  # <-- arguments 是序列化后的 JSON Object，我们需要使用 json.loads 反序列>化一下
                if tool_call_name == "$web_search":
                    if verbose:print_cn("WEB | searching internet ...\n")
                    tool_result = search_impl(tool_call_arguments)
                else:
                    tool_result = f"Error: unable to find tool by name '{tool_call_name}'"

                # 使用函数执行结果构造一个 role=tool 的 message，以此来向模型展示工具调用的结果；
                # 注意，我们需要在 message 中提供 tool_call_id 和 name 字段，以便 Kimi 大模型
                # 能正确匹配到对应的 tool_call。
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call_name,
                    "content": json.dumps(tool_result),  # <-- 我们约定使用字符串格式向 Kimi 大模型提交工具调用结果，因此在这里使用 json.dumps 将执行结果序列化成字符串
                })
    result=choice.message.content
    if verbose:print_cn('-'*30+'\n\n')
    if verbose:
        print_cn(result)
    else:
        print_cn_all(result)
    print('')
    return(result)






#######
# RAG

def generate_keyword(new_content,verbose=True):
    if verbose: print_cn('RAG | preparing ...\n')
    key_prompt = f"""
        <User_Message>
        {new_content}
        </User_Message>
        """ + RAG_KEYWORD_PROMPT
    this_message=[{"role":"user","content":key_prompt}]
    completion = client.chat.completions.create(
            model = RAG_KEYWORD_MODEL,
            messages = this_message,
            temperature = RAG_KEYWORD_TEMPERATURE,
            )
    key_content=completion.choices[0].message.content
    if verbose: print_cn('RAG | content: ' + key_content +'\n')
    return key_content


def retrieve_keyword(key_content, verbose=True):
    if verbose: print_cn('RAG | retrieving ...\n')
    vectorstore = build_vectorstore()
    if vectorstore is not None:
        retrieved_docs = vectorstore.similarity_search(key_content, k=VECTOR_K)
        #print(retrieved_docs)
        retrieved_content = "\n".join(["file_path: "+doc.metadata.get('file_path','') + '\n' +
                                       "chunk_idx: "+str(doc.metadata.get('chunk_idx','')) + '\n' + 
                                       "page_content: "+doc.page_content for doc in retrieved_docs])
        retrieved_docpaths_list = [doc.metadata.get('file_path', '') for doc in retrieved_docs]
        retrieved_chunkidx_list = [doc.metadata.get('chunk_idx', '') for doc in retrieved_docs]
        if verbose:
            print_cn("RAG | retrieved docs:\n")
            i=0
            while i <len(retrieved_docpaths_list):
                print_cn_all("RAG | " + 'chunk_idx: ' + str(retrieved_chunkidx_list[i])+
                                " | " + retrieved_docpaths_list[i] + '\n')
                i=i+1
        return retrieved_content
    else:
        return None



def doublecheck_retrieved_content(retrieved_content, key_content, verbose=True):
    if verbose: print_cn("RAG | double-check ...\n")
    
    # 结构化输入，使用清晰的分隔符
    ori_content = f"""
        <Retrieval_Content>
        {retrieved_content}
        </Retrieval_Content>
        
        <Retrieval_Keywords>
        {key_content}
        </Retrieval_Keywords> 
        """ + RAG_CHECK_PROMPT
    
    this_message = [{"role": "user", "content": ori_content}]
    
    completion = client.chat.completions.create(
        model=RAG_CHECK_MODEL,
        messages=this_message,
        temperature= RAG_CHECK_TEMPERATURE, # 审查任务建议温度设为 0，保证稳定性
    )
    
    check_content = completion.choices[0].message.content.strip()

    is_no = check_content.lower().replace('.', '') == 'no'

    if is_no:
        if verbose: print_cn('RAG | no reference is used.\n')
        return "No"
    
    return check_content




def retrieve_rag(new_messages, doublecheck=True, verbose=True):
    new_content=new_messages[0]['content']
    key_content=generate_keyword(new_content,verbose=verbose)
    if key_content != 'No' and key_content:
        retrieved_content=retrieve_keyword(key_content, verbose=verbose)
        if retrieved_content:
            if doublecheck:
                check_content = doublecheck_retrieved_content(retrieved_content,key_content,verbose)
            ############################
            if doublecheck:
                if check_content =='No':
                    if verbose:print_cn('-'*30+'\n\n')
                    return new_messages
                update_reference=check_content                
            else:
                update_reference=retrieved_content
            if verbose : print_cn('RAG | used length: '+str(len(update_reference))+'\n')
            ############################
            update_input=new_content
            update_content = f"""
                <References>
                {update_reference}
                </References>

                <User_Message>
                {update_input}
                </User_Message>
                """ + RAG_ANSWER_PROMPT
            new_messages[0]['content'] = update_content
    if verbose:print_cn('-'*30+'\n\n')
    return new_messages



def search_web(messages, verbose=True):
    if verbose:
        print_cn("WEB | checking ...\n")
    finish_reason = None
    while finish_reason is None or finish_reason == "tool_calls":
        choice = chat(messages)
        finish_reason = choice.finish_reason
        if finish_reason == "tool_calls":  # <-- 判断当前返回内容是否包含 tool_calls
            messages.append(choice.message)  # <-- 我们将 Kimi 大模型返回给我们的 assistant 消息也添加到上下文中，以便于下次请求时 Kimi 大模型能理解我们>的诉求
            for tool_call in choice.message.tool_calls:  # <-- tool_calls 可能是多个，因此我们使用循环逐个执行
                tool_call_name = tool_call.function.name
                tool_call_arguments = json.loads(tool_call.function.arguments)  # <-- arguments 是序列化后的 JSON Object，我们需要使用 json.loads 反序列>化一下
                if tool_call_name == "$web_search":
                    if verbose:print_cn("WEB | searching internet ...\n")
                    tool_result = search_impl(tool_call_arguments)
                else:
                    tool_result = f"Error: unable to find tool by name '{tool_call_name}'"

                # 使用函数执行结果构造一个 role=tool 的 message，以此来向模型展示工具调用的结果；
                # 注意，我们需要在 message 中提供 tool_call_id 和 name 字段，以便 Kimi 大模型
                # 能正确匹配到对应的 tool_call。
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call_name,
                    "content": json.dumps(tool_result),  # <-- 我们约定使用字符串格式向 Kimi 大模型提交工具调用结果，因此在这里使用 json.dumps 将执行结果序列化成字符串
                })
    result=choice.message.content
    
    if verbose:print_cn('-'*20+'\n')
    messages[0]['content'] =f'''
        <Answers_After_Web_Search>
        {result}
        </Answers_After_Web_Search> 
        
        <User_Message>
        {messages[0]['content']}
        </User_Message>
        '''
    return(messages)



