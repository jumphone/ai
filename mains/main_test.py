from .common_imports import *
from src.enc import *
from src.rag import *


################################
def run():
    print('test')
    #embeddings=init_huggingface_embeddings( SEARCH_MODEL_PATH )
    build_vectorstore()
    #this_message=[{"role":"user","content":'你是谁'}]
    #retrieve_rag(this_message)
    


def test2():
    #embeddings = HuggingFaceEmbeddings(model_name=MULTI_MODEL_PATH)
    embeddings = init_huggingface_embeddings( MULTI_MODEL_PATH )
    vectorstore = load_faiss_vectorstore(embeddings)

    question='函数是什么'

    retrieved_docs = vectorstore.similarity_search(question, k=VECTOR_K)
    retrieved_context = "\n".join([doc.page_content for doc in retrieved_docs])
    print(retrieved_context)


def test():
    file_path = os.path.join(DB_FOLDER, "biuh_rule.txt")
    documents = load_text_file(file_path)
    if not documents:
        exit(1)

    text_splitter = CharacterTextSplitter(
        separator="\n",  # 按换行拆分
        chunk_size=500,  # 每个文本块500字符
        chunk_overlap=50  # 重叠50字符保证连贯
        )

    splits = split_documents(text_splitter, documents)
    split_texts = [doc.page_content for doc in splits]
    split_metadatas = [doc.metadata for doc in splits]
    print(split_texts)

    #embed_model = SentenceTransformer(MULTI_MODEL_PATH.rstrip("/"))
    embeddings = HuggingFaceEmbeddings(
        model_name=MULTI_MODEL_PATH,
        )

    vectorstore = FAISS.from_texts(
        texts=split_texts,
        embedding=embeddings,
        metadatas=split_metadatas  # 传入拆分后的元数据
        )
    question='test 有什么内容'
    retrieved_docs = vectorstore.similarity_search(question, k=3)
    context = "\n".join([doc.page_content for doc in retrieved_docs])
    print(context)



