import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_openai_embeddings():
    # Create a mock for the OpenAIEmbeddings *instance*
    mock_embedding_instance = MagicMock()
    # Configure the embed_documents method of the mock instance
    mock_embedding_instance.embed_documents.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    
    # Create a mock for the OpenAIEmbeddings *class*
    # When the class is called (instantiated), it returns our mock instance
    mock_embedding_class = MagicMock(return_value=mock_embedding_instance)
    return mock_embedding_class

@pytest.fixture
def mock_openai_chat_llm():
    mock = MagicMock()
    mock.stream.return_value = [MagicMock(content="mocked response")]
    return mock