import pytest
from app.retriever import get_retriever, add_documents_to_vectorstore
from langchain_core.documents import Document
from unittest.mock import patch, MagicMock
import os
import shutil
import chromadb

# Define a temporary directory for ChromaDB persistence
TEST_CHROMA_DIR = "./test_vector_store"

@pytest.fixture(autouse=True)
def setup_and_teardown_chroma_dir():
    # Setup: Create a clean directory before each test
    if os.path.exists(TEST_CHROMA_DIR):
        shutil.rmtree(TEST_CHROMA_DIR)
    os.makedirs(TEST_CHROMA_DIR)
    yield
    # Teardown: Clean up the directory after each test
    if os.path.exists(TEST_CHROMA_DIR):
        shutil.rmtree(TEST_CHROMA_DIR)

@patch('app.retriever.OpenAIEmbeddings')
def test_get_retriever(mock_openai_embeddings, mock_openai_chat_llm):
    # Configure the mock to return a mock embedding function
    mock_openai_embeddings.return_value = mock_openai_embeddings

    retriever = get_retriever(persist_directory=TEST_CHROMA_DIR)
    assert retriever is not None
    # You can add more assertions here to check retriever's configuration

@patch('app.retriever.OpenAIEmbeddings')
@patch('app.retriever.chromadb.PersistentClient')
@patch('app.retriever.Chroma')
def test_add_documents_to_vectorstore(mock_chroma_class, mock_persistent_client, mock_openai_embeddings):
    docs = [Document(page_content="test document 1"), Document(page_content="test document 2")]

    # Configure the mock for OpenAIEmbeddings
    mock_openai_embeddings.return_value.embed_documents.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

    # Configure the mock Chroma class
    mock_chroma_instance = MagicMock()
    mock_chroma_class.return_value = mock_chroma_instance

    # Call the function under test
    add_documents_to_vectorstore(docs, persist_directory=TEST_CHROMA_DIR)

    # Assertions
    mock_persistent_client.assert_called_once_with(path=TEST_CHROMA_DIR)
    mock_chroma_class.assert_called_once_with(
        client=mock_persistent_client.return_value,
        collection_name="default_collection",
        embedding_function=mock_openai_embeddings.return_value,
    )
    mock_chroma_instance.add_documents.assert_called_once_with(docs)
