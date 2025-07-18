import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.retriever import add_documents_to_vectorstore

CHROMA_PERSIST_DIRECTORY = "./vector_store"

def embed_pdfs_in_directory(directory_path: str, collection_name: str = "default_collection"):
    documents = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory_path, filename)
            print(f"Loading {file_path}...")
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())

    if not documents:
        print(f"No PDF documents found in {directory_path}")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    add_documents_to_vectorstore(chunks, collection_name, persist_directory=CHROMA_PERSIST_DIRECTORY)
    print("PDFs embedded successfully!")

if __name__ == "__main__":
    # This assumes your PDFs are in the data/pdfs directory relative to the project root
    # You might need to adjust this path based on where you run the script
    pdf_directory = "./data/pdfs"
    embed_pdfs_in_directory(pdf_directory)
