from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config import VECTOR_STORE_DIR, EMBEDDING_MODEL

def load_retriever(k=15):
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vector_store = FAISS.load_local(
        str(VECTOR_STORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True
    )
    return vector_store.as_retriever(search_kwargs={"k": k})