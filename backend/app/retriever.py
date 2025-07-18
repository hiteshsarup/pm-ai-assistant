import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from typing import List
import chromadb

def get_retriever(collection_name: str = "default_collection", persist_directory: str = "./vector_store"):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    os.makedirs(persist_directory, exist_ok=True)
    
    client = chromadb.PersistentClient(path=persist_directory)

    vectorstore = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embeddings,
    )
    
    return vectorstore.as_retriever(search_kwargs={"k": 20})

def add_documents_to_vectorstore(documents: List[Document], collection_name: str = "default_collection", persist_directory: str = "./vector_store"):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    os.makedirs(persist_directory, exist_ok=True)

    client = chromadb.PersistentClient(path=persist_directory)

    vectorstore = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embeddings,
    )
    vectorstore.add_documents(documents)
    print(f"Added {len(documents)} documents to ChromaDB collection: {collection_name}")