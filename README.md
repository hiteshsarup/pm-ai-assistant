# Shipsy PM Agent

## MVP v0.1

This is a single-user web application designed to assist product managers at a B2B SaaS TMS company with generating new Product Requirements Documents (PRDs) and reviewing existing PRDs.

## Architecture Diagram

```mermaid
graph TD
    User[User] -->|Accesses| Frontend(Next.js React UI)
    Frontend -->|API Calls| Nginx[Nginx Reverse Proxy]
    Nginx -->|Proxies /chat, /upload| Backend(FastAPI Server)
    Backend -->|Uses| LangChain[LangChain]
    LangChain -->|Embeddings| OpenAI_Embed[OpenAI Embeddings]
    LangChain -->|LLM Calls| OpenAI_GPT[OpenAI GPT-4o-mini]
    LangChain -->|Vector Store| ChromaDB[ChromaDB (local persistence)]
    Backend -->|Stores| Conversations[conversations/ (JSON transcripts)]
    User -->|Uploads PDFs| Backend
    Backend -->|Stores PDFs temporarily| Data_PDFs[data/pdfs/]
    Data_PDFs -->|Processed by| Backend
    Backend -->|Stores embeddings| Vector_Store[vector_store/]
```

## Quick Start

To get the Shipsy PM Agent running locally, follow these steps:

1.  **Prerequisites:**
    *   Docker Desktop installed and running.
    *   An OpenAI API Key.

2.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd pm-ai-agent
    ```

3.  **Configure your OpenAI API Key:**
    Create a `.env` file in the root of the project and add your OpenAI API key:
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ```

4.  **Build and Run with Docker Compose:**
    ```bash
    docker-compose up --build -d
    ```
    This command will:
    *   Build the Docker images for the frontend and backend services.
    *   Start the backend (FastAPI) on `http://localhost:8000`.
    *   Start the frontend (Next.js) on `http://localhost:3000`.
    *   Start Nginx as a reverse proxy on `http://localhost:80`.

5.  **Access the Application:**
    Open your web browser and navigate to `http://localhost:3000` (for direct frontend access) or `http://localhost:80` (via Nginx).

## Embedding Knowledge-Base PDFs

To provide context to the LLM, you can embed PDF documents into the ChromaDB vector store. Place your PDF files in the `./data/pdfs/` directory.

Then, run the embedding script from within the backend container:

```bash
# First, ensure your containers are running
docker-compose up -d

# Execute the embedding script inside the backend container
docker-compose exec backend python scripts/embed_pdfs.py
```

## Future Work (Nice-to-have later)

*   **Database Flexibility:** Implement an environment flag to swap ChromaDB with Postgres/pgvector.
*   **Multi-user Support:** Integrate Auth0 for user authentication and manage user-specific data.
*   **Content Ingestion:** Support Confluence HTML imports via a background worker (e.g., Celery or FastAPI background tasks).
*   **Observability:** Enable OpenTelemetry tracing for LLM calls.
*   **Deployment Readiness:** Expose REST `/health` and `/metrics` endpoints for Kubernetes readiness checks.

## Development

### Running Tests

To run the backend tests (pytest):

```bash
docker-compose exec backend pytest /app/tests
```

### Code Formatting and Linting

This project uses `ruff`, `black`, and `isort` for Python code formatting and linting, and `eslint` for TypeScript/React. It is recommended to set up `pre-commit` hooks to automatically run these checks before committing.

1.  **Install pre-commit:**
    ```bash
    pip install pre-commit
    ```
2.  **Install the git hooks:**
    ```bash
    pre-commit install
    ```
