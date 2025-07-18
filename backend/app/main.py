import os
import json
import uuid
from datetime import datetime
from typing import List, Dict

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from operator import itemgetter
import tiktoken

from app.schemas import ChatRequest, Message, UploadResponse
from app.prompts import SYSTEM_PROMPT, chat_prompt
from app.retriever import get_retriever, add_documents_to_vectorstore

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Allow frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
# from dotenv import load_dotenv
# load_dotenv() # This is handled by docker-compose for now

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# Initialize LLM
llm = ChatOpenAI(model=MODEL_NAME, openai_api_key=OPENAI_API_KEY, streaming=True)

# Directory for storing chat transcripts
CONVERSATIONS_DIR = "./conversations"
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

# ChromaDB persistence directory
CHROMA_PERSIST_DIRECTORY = "./vector_store"

# Initialize tiktoken encoder
encoding = tiktoken.encoding_for_model(MODEL_NAME)

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

# Helper function to format documents for the prompt
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    try:
        # Save the uploaded file temporarily
        file_location = f"./data/pdfs/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        # Load and split the document
        loader = PyPDFLoader(file_location)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        chunks = text_splitter.split_documents(documents)

        # Add to vector store
        add_documents_to_vectorstore(chunks, persist_directory=CHROMA_PERSIST_DIRECTORY)

        # Clean up temporary file
        os.remove(file_location)

        return {"filename": file.filename, "status": "success", "message": f"Processed {len(chunks)} chunks from {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {e}")

@app.post("/chat")
async def chat(request: ChatRequest):
    session_id = str(uuid.uuid4())
    transcript_file = os.path.join(CONVERSATIONS_DIR, f"{session_id}.json")

    # Convert Pydantic messages to LangChain messages
    langchain_messages = []
    for msg in request.messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        else:
            langchain_messages.append(AIMessage(content=msg.content))

    # Truncate chat history to fit within token limits
    # Max 16k tokens for gpt-4o-mini, leaving room for retrieved docs and current input
    MAX_TOKENS = 50000
    current_tokens = count_tokens(SYSTEM_PROMPT) + count_tokens(request.messages[-1].content)
    
    # Estimate tokens for retrieved docs (rough estimate, actual will vary)
    # Assuming max 20 docs * 1000 tokens/doc = 20000 tokens
    # This needs to be more dynamic with actual retrieval
    retrieved_docs_token_estimate = 20000 

    history_tokens = 0
    truncated_history = []
    # Iterate from oldest to newest to truncate
    for msg in reversed(langchain_messages[:-1]): # Exclude the latest user message
        msg_content = msg.content if isinstance(msg, (HumanMessage, AIMessage)) else str(msg)
        tokens = count_tokens(msg_content)
        if current_tokens + history_tokens + tokens + retrieved_docs_token_estimate < MAX_TOKENS:
            history_tokens += tokens
            truncated_history.insert(0, msg) # Add to the beginning to maintain order
        else:
            break

    final_chat_history = truncated_history

    # Get retriever (using default collection for now)
    retriever = get_retriever(persist_directory=CHROMA_PERSIST_DIRECTORY)

    # Construct RAG chain
    rag_chain = (
        {
            "context": itemgetter("input") | retriever | format_docs,
            "chat_history": itemgetter("chat_history"),
            "input": itemgetter("input"),
        }
        | chat_prompt
        | llm
        | StrOutputParser()
    )

    async def generate_response():
        full_response_content = ""
        try:
            async for chunk in rag_chain.astream({"input": request.messages[-1].content, "chat_history": final_chat_history}):
                full_response_content += chunk
                yield chunk
        except Exception as e:
            print(f"Error during streaming: {e}")
            yield f"Error: {e}"
        finally:
            # Save chat transcript after response is complete
            # This will save the full conversation including the AI's response
            request.messages.append(Message(role="assistant", content=full_response_content))
            with open(transcript_file, "w") as f:
                json.dump(request.dict(), f, indent=2)

    return StreamingResponse(generate_response(), media_type="text/event-stream")
