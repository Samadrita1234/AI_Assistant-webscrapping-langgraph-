import os
import json
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

VECTORSTORE_PATH = "faiss_index"

with open("chunks.json", "r", encoding="utf-8") as f:
    chunk_texts = json.load(f)

docs = [Document(page_content=text) for text in chunk_texts]

embeddings = OllamaEmbeddings(model="mistral")

if not os.path.exists(VECTORSTORE_PATH):
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(VECTORSTORE_PATH)
    
    print("FAISS vectorstore created and saved!")
else:
    print("FAISS vectorstore already exists.")
