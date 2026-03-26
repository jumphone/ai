from .common_imports import *
from src.rag import *

################################
def run():
    print('build RAG index ...')
    build_vectorstore(force=True) 
    print('finished!')


