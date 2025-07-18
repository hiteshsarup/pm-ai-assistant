import pytest
from app.prompts import SYSTEM_PROMPT, chat_prompt
from langchain_core.messages import HumanMessage, AIMessage

def test_system_prompt_content():
    assert "Shipsy Product-Head" in SYSTEM_PROMPT
    assert "generate new Product Requirements Documents (PRDs)" in SYSTEM_PROMPT
    assert "review existing PRDs, suggesting fixes." in SYSTEM_PROMPT # Corrected assertion

def test_chat_prompt_structure():
    # Test with a simple input and chat history
    messages = [
        HumanMessage(content="Hello"),
        AIMessage(content="Hi there!")
    ]
    
    # The chat_prompt expects 'input' and 'chat_history' variables
    # When used in a chain, these are typically passed through.
    # For direct testing, we can simulate the input.
    formatted_prompt = chat_prompt.format_messages(
        input="What is a PRD?", 
        chat_history=messages
    )
    
    assert len(formatted_prompt) == 4 # System, Human, AI, Human (new input)
    assert formatted_prompt[0].content == SYSTEM_PROMPT
    assert formatted_prompt[1].content == "Hello"
    assert formatted_prompt[2].content == "Hi there!"
    assert formatted_prompt[3].content == "What is a PRD?"

    assert formatted_prompt[0].type == "system"
    assert formatted_prompt[1].type == "human"
    assert formatted_prompt[2].type == "ai"
    assert formatted_prompt[3].type == "human"