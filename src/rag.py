from .prepare import *

##########
# RAG
#########
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from io import StringIO
import httpx,warnings,logging, pickle, shutil



def init_huggingface_embeddings():
    model_path = SEARCH_MODEL_PATH.rstrip("/")
    
    # 1. 屏蔽 Python 警告 (针对 "No sentence-transformers model found")
    warnings.filterwarnings("ignore", category=UserWarning)
    
    # 2. 屏蔽 Transformers 库的输出
    from transformers import logging as tf_logging
    tf_logging.set_verbosity_error()
    
    # 3. 屏蔽 LangChain 的日志
    logging.getLogger("langchain_huggingface").setLevel(logging.ERROR)
    logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

    # 4. 屏蔽环境变量 (针对进度条和 Tokenizer 并行警告)
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["TRANSFORMERS_VERBOSITY"] = "error"
    # 隐藏 tqdm 进度条
    os.environ["SENTENCE_TRANSFORMERS_HOME"] = model_path # 确保路径指向正确

    # 5. 核心：如果它还报 "No sentence-transformers model found"
    # 往往是因为你的路径下缺少 modules.json 或 sentence_bert_config.json
    # 我们可以通过指定特定的类来初始化，绕过探测逻辑
    old_stderr = sys.stderr
    sys.stderr = StringIO()
    embeddings = HuggingFaceEmbeddings(
        model_name=model_path,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
        )
    sys.stderr = old_stderr
    return embeddings


def batch_load_files():
    folder_path=RAG_SRC_DATABASE
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    splits = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and os.path.splitext(file_name)[1].lower() in SUPPORTED_EXT:
            with open(file_path, "r", encoding="utf-8") as f:
                text=f.read().rstrip()
            if not text:
                continue
            doc_splits = splitter.create_documents(texts=[text],
                         metadatas=[{"source":file_name, "file_path":file_path}]
                         )
            max_idx=len(doc_splits)-1
            for idx, chunk in enumerate(doc_splits):
                chunk.metadata["chunk_idx"] = idx
            splits.extend(doc_splits)
    return splits



def build_vectorstore(force=False):
    vectorstore_folder = RAG_SRC_VECTOR
    embeddings = init_huggingface_embeddings()

    # 1. 强制重建 = 删除旧目录
    if force and os.path.exists(vectorstore_folder):
        shutil.rmtree(vectorstore_folder)

    # 2. 存在就直接加载 
    if os.path.exists(vectorstore_folder):
        vectorstore = FAISS.load_local(
            vectorstore_folder,
            embeddings,
            allow_dangerous_deserialization=True
            )
        return vectorstore

    # 3. 不存在才读文件、建库
    splits = batch_load_files()
    
    # 使用 from_documents 创建索引
    vectorstore = FAISS.from_documents(
        splits, 
        embeddings
        )
    
    # 持久化到本地路径
    vectorstore.save_local(vectorstore_folder)

    return vectorstore









