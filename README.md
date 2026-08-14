\# SafeRAG



\### A Safety-Aware Retrieval-Augmented Generation System for Policy and Operational Documents



SafeRAG is a production-oriented Retrieval-Augmented Generation (RAG) system designed to answer questions from a controlled collection of hospital and pharmacy policy documents.



Unlike a basic RAG pipeline that simply retrieves the most similar documents and sends them to an LLM, SafeRAG adds:



\- Metadata-aware semantic retrieval

\- MMR-based retrieval for diverse context

\- Document chunking with metadata preservation

\- Conflict detection between multiple policy versions

\- Temporal resolution to identify the authoritative document

\- Grounded Gemini generation

\- Source attribution

\- Dockerized deployment

\- Automated unit and integration tests



The system is designed around an important principle:



> \*\*If the required information cannot be supported by the provided documents, SafeRAG should not invent an answer.\*\*







\## Features:



1\. Document Ingestion:


SafeRAG processes PDF documents through an ingestion pipeline:


PDF Documents

     ↓

PDF Loader

     ↓

Metadata Enrichment

     ↓

Document Chunking

     ↓

Embedding Generation

     ↓

Chroma Vector Database



Each document is enriched with metadata such as:



Document ID

Document name

Document date

Page number

Department

Document type



This metadata is preserved during chunking and used later during retrieval and reasoning.











2\. Semantic Retrieval:



SafeRAG uses Hugging Face embeddings with:



BAAI/bge-small-en-v1.5



Documents are stored in Chroma and retrieved using semantic similarity.



The retrieval layer uses Maximum Marginal Relevance (MMR):



Top K       = 5

Fetch K     = 20

MMR Lambda  = 0.7



MMR helps balance relevance and diversity so that the retrieved context does not contain unnecessarily repetitive chunks.











3\. Metadata-Aware Retrieval:


Queries can optionally be restricted using metadata filters.

For example:


{

"question": "What is the current pharmacy dispensing target?",

"department": "pharmacy"

}





The retrieval system can filter documents by:



department

document\_type

This allows SafeRAG to narrow the search space before generating an answer.






4\. Conflict Detection:

Policy documents may contain multiple versions of the same policy.






For example:



January 2026 Policy

       ↓

30-minute dispensing target





March 2026 Policy Update

       ↓

20-minute dispensing target





A naive RAG system may retrieve both documents and provide an ambiguous answer.



SafeRAG detects conflicts by grouping documents using:


Department + Document Type:

It then checks whether multiple document versions exist for the same policy category.













5\. Temporal Resolution:

When multiple versions of a policy are retrieved, SafeRAG uses document dates to identify the authoritative document.






The pipeline is:



Retrieved Documents

       ↓

Conflict Detection

       ↓

Multiple Versions?

       ↓

Temporal Resolution

       ↓

Authoritative Document



This is particularly important for questions such as:

What was the pharmacy dispensing target in January 2026?



versus:

What is the current pharmacy dispensing target?

The system can distinguish between historical and current policy information using document metadata.













6\. Grounded Generation:

SafeRAG uses Google's Gemini API for final answer generation.




Configured model:

gemini-3.5-flash





The generator receives:



  User Question

        +

Retrieved / Resolved Context

        ↓

      Gemini

        ↓

    Grounded Answer



The generation prompt explicitly instructs the model to:


Use only the supplied context

Avoid outside knowledge

Avoid inventing facts, dates, numbers, or policies

Return a fallback response when the context is insufficient

Prefer authoritative resolved information

Prefer the latest explicitly effective policy when applicable

Keep answers concise and factual




If the provided context is insufficient, the system instructs Gemini to return:


I couldn't find sufficient information in the provided documents.

This reduces unsupported generation and hallucination risk.











System Architecture:



                            ┌──────────────────┐

                            │     User Query   │

                            └────────┬─────────┘

                                     │

                                     ▼

                            ┌──────────────────┐

                            │     FastAPI      │

                            │    /query API    │

                            └────────┬─────────┘

                                     │

                                     ▼

                            ┌──────────────────┐

                            │    Retrieval     │

                            │  Semantic + MMR  │

                            └────────┬─────────┘

                                     │

                                     ▼

                            ┌──────────────────┐

                            │ Conflict Detector│

                            └────────┬─────────┘

                                     │

                                     ▼

                            ┌──────────────────┐

                            │ Temporal Resolver│

                            └────────┬─────────┘

                                     │

                                     ▼

                            ┌──────────────────┐
                            │ Grounded Context │

                            └────────┬─────────┘

                                     │

                                     ▼

                            ┌──────────────────┐

                            │ Gemini Generator │

                            └────────┬─────────┘

                                     │

                                     ▼

                       ┌──────────────────────────┐

                       │ Answer + Sources + Status│

                        └──────────────────────────┘











End-to-End RAG Pipeline:

The complete SafeRAG pipeline is implemented as:



Query

    ↓

Retrieval

    ↓

Conflict Detection

    ↓

Temporal Resolution

    ↓

Grounded Generation







Step 1 — Retrieval:

The system searches the Chroma vector store for relevant documents.




Step 2 — Conflict Detection:

Retrieved documents are checked for multiple versions of the same policy category.




Step 3 — Temporal Resolution:

If conflicting versions exist, the system attempts to identify the authoritative document using document dates.




Step 4 — Context Construction:

Relevant document content and metadata are converted into a structured context containing:


SOURCE

DOCUMENT ID

DOCUMENT DATE

PAGE

CONTENT



Step 5 — Grounded Generation:

The structured context is passed to Gemini together with the user's question.




Step 6 — Response:

The API returns:


{

    "answer": "...",

    "sources": \[],

    "conflict\_detected": false

}













API:

SafeRAG exposes a lightweight FastAPI service.



Health Check:

GET /health



Example:


{

    "status": "healthy",

    "service": "SafeRAG",

    "environment": "development"

}








Query:

POST /query:

Content-Type: application/json



Request:


{

    "question": "What is the current pharmacy dispensing target?",

    "department": "pharmacy"

}



Response:



{

    "answer": "The current pharmacy dispensing target is 20 minutes.",

    "sources": \[

        {

        "document\_id": "PHARM-2026-03",

        "document\_name": "04\_pharmacy\_policy\_march\_update.pdf",

        "document\_date": "2026-03-15",

        "page": 1

        }

    ],

    "conflict\_detected": true

}











Example Queries:

Current Policy:

What is the current pharmacy dispensing target?

SafeRAG can identify the latest authoritative pharmacy policy.



Historical Policy:

What was the pharmacy dispensing target in January 2026?

SafeRAG can retrieve the January policy version instead of automatically returning the latest policy.







Department Filtering:

{

&#x20; "question": "What is the dispensing target?",

&#x20; "department": "pharmacy"

}


The query is restricted to the specified department.






Project Structure:



SafeRAG/

│

├── app/

│   ├── api/

│   │   └── main.py

│   │

│   ├── config/

│   │   └── settings.py

│   │

│   ├── evaluation/

│   │

│   ├── ingestion/

│   │   ├── chunker.py

│   │   ├── metadata.py

│   │   └── pipeline.py

│   │

│   ├── models/

│   │   └── schemas.py

│   │

│   ├── reasoning/

│   │   ├── conflict.py

│   │   ├── generator.py

│   │   ├── rag\_pipeline.py

│   │   └── temporal.py

│   │

│   ├── retrieval/

│   │   ├── embeddings.py

│   │   ├── indexer.py

│   │   ├── retriever.py

│   │   └── vector\_store.py

│   │

│   ├── safety/

│   │   └── prompt\_guard.py

│   │

│   └── utils/

│       └── logging.py

│

├── data/

│   ├── evaluation/

│   └── raw/

│

├── scripts/

│   ├── check\_vector\_store.py

│   ├── generate\_dataset.py

│   ├── index\_documents.py

│   ├── test\_conflict.py

│   ├── test\_generator.py

│   ├── test\_rag\_pipeline.py

│   ├── test\_retrieval.py

│   └── test\_temporal.py

│

├── tests/

│   ├── integration/

│   │   └── test\_api.py

│   │

│   └── unit/

│       ├── test\_dataset.py

│       └── test\_ingestion.py

│

├── Dockerfile

├── docker-compose.yml

├── requirements.txt

├── .env.example

└── README.md











Configuration:

SafeRAG uses environment-based configuration through .env.



Example:

GEMINI\_API\_KEY=your\_api\_key\_here

GEMINI\_MODEL=gemini-2.5-flash



EMBEDDING\_MODEL=BAAI/bge-small-en-v1.5

EMBEDDING\_VERSION=v1



CHROMA\_PERSIST\_DIR=./chroma\_data

CHROMA\_COLLECTION=saferag\_documents



TOP\_K=5

FETCH\_K=20

MMR\_LAMBDA=0.7



CHUNK\_SIZE=500

CHUNK\_OVERLAP=100



Security:

The actual .env file is intentionally excluded from Git using .gitignore.



Only .env.example is committed.

Never commit:



GEMINI\_API\_KEY

or any other secret credentials.













Running Locally:

1\. Clone the repository:

git clone https://github.com/MananPatel52/SafeRAG.git

cd SafeRAG



2\. Create a virtual environment:

Windows:

python -m venv .venv

.venv\\Scripts\\Activate.ps1



Linux/macOS:

python -m venv .venv

source .venv/bin/activate




3\. Install dependencies:

pip install -r requirements.txt




4\. Configure environment variables:

Create a .env file:

GEMINI\_API\_KEY=your\_api\_key\_here



Additional configuration can be copied from:

.env.example



5\. Index the documents

python scripts/index\_documents.py

This processes the PDFs, creates chunks, generates embeddings, and indexes the documents into Chroma.





6\. Start the API

uvicorn app.api.main:app --reload --port 8000

The API will be available at:

http://localhost:8000











Running with Docker

SafeRAG includes Docker support for reproducible deployment.



Build and start

docker compose up --build



The API will be available at:

http://localhost:8000



Check running services

docker compose ps



View logs

docker compose logs --tail=50 saferag



Stop the application

docker compose down

The Chroma database is persisted through the Docker Compose volume mapping:

./chroma\_data:/app/chroma\_data







Testing:

SafeRAG includes unit and integration tests.

Run the complete test suite: python -m pytest -v



The current test suite covers:


API health endpoint

Query endpoint

Query validation

Pharmacy policy queries

Historical policy queries

Current policy queries

Unsupported questions

Internal error handling

Dataset loading

PDF ingestion

Metadata enrichment

Document chunking

Example result: 13 passed













Design Decisions:

Why RAG?

The system answers questions against a controlled document collection instead of relying entirely on the model's pretrained knowledge.


This provides:

Document-grounded answers

Source attribution

Easier policy updates

Reduced hallucination risk




Why MMR?

Pure similarity search can return highly redundant chunks.

MMR helps retrieve relevant but more diverse information.





Why metadata?

Policy documents often have:


Different departments

Different document types

Different dates

Multiple revisions

Metadata enables more precise retrieval and reasoning.





Why conflict detection?

A policy knowledge base can contain multiple versions of the same policy.

Without conflict detection, the model may combine outdated and current information.




Why temporal resolution?

The latest document is not always the correct answer for a historical question.







Temporal reasoning allows SafeRAG to distinguish between:

"What is the current policy?"

and:

"What was the policy in January 2026?"







Safety Principles:



SafeRAG is designed around grounded generation.



The generator is instructed to:



Use only the supplied context.

Do not use outside knowledge.

Do not invent facts.

Do not invent dates.

Do not invent policies.

Do not invent sources.



When sufficient information is unavailable, the system returns:

I couldn't find sufficient information in the provided documents.


This makes the system more suitable for document-driven policy question answering where unsupported answers can be problematic.













Tech Stack:


| Component           | Technology             |

| ------------------- | ---------------------- |

| API                 | FastAPI                |

| Language            | Python                 |

| LLM                 | Google Gemini          |

| LLM Model           | gemini-2.5-flash       |

| Embeddings          | BAAI/bge-small-en-v1.5 |

| Vector Database     | Chroma                 |

| Retrieval           | Semantic Search + MMR  |

| Document Processing | PDF Loader             |

| Validation          | Pydantic               |

| Testing             | Pytest                 |

| Containerization    | Docker                 |

| Orchestration       | Docker Compose         |







Potential future improvements include:


Authentication and authorization

More comprehensive evaluation metrics

Retrieval quality benchmarking

Reranking models

Better observability and tracing

Production-grade secret management

Persistent external vector database

Streaming responses

Rate limiting

API documentation and authentication

Automated CI/CD deployment

Larger document evaluation datasets











Author: Manan Kansagara

Computer Science Graduate

GitHub: https://github.com/MananPatel52




License

This project is intended for educational, portfolio, and demonstration purposes.
