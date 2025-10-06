# Multi-Document Search Engine - Visual System Diagram

## 🎨 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                                                                 │
│  query_documents("Your question")                              │
│            OR                                                   │
│  query_specific_type("Your question", "pdf")                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MULTI-ROUTE CHAIN                            │
│                   (Orchestrator Layer)                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ROUTER CHAIN                               │
│                   (LLM-Based Router)                            │
│                                                                 │
│  Analyzes query → Determines document type                     │
│                                                                 │
│  "sales data" → CSV                                            │
│  "report findings" → PDF                                       │
│  "meeting notes" → DOCX                                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │ PDF Chain   │ │ DOCX Chain  │ │ CSV Chain   │
    │             │ │             │ │             │
    │ RetrievalQA │ │ RetrievalQA │ │ RetrievalQA │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │PDF Retriever│ │DOCX Retriever│ │CSV Retriever│
    │   (k=5)     │ │   (k=5)     │ │   (k=10)    │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │PDF VectorDB │ │DOCX VectorDB│ │CSV VectorDB │
    │             │ │             │ │             │
    │DocArray     │ │DocArray     │ │DocArray     │
    │In-Memory    │ │In-Memory    │ │In-Memory    │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │PDF Documents│ │Word Documents│ │CSV Files    │
    │  (*.pdf)    │ │  (*.docx)   │ │  (*.csv)    │
    │             │ │             │ │             │
    │ • Reports   │ │ • Memos     │ │ • Sales     │
    │ • Papers    │ │ • Letters   │ │ • Orders    │
    │ • Manuals   │ │ • Proposals │ │ • Data      │
    └─────────────┘ └─────────────┘ └─────────────┘
```

## 🔄 Query Flow Diagram

```
User Query: "What are the total sales for 2016?"
    │
    │ Step 1: Query received
    ▼
┌─────────────────────────────────────┐
│ MultiRouteChain                     │
│ • Receives query                    │
│ • Passes to router                  │
└────────────┬────────────────────────┘
             │ Step 2: Route query
             ▼
┌─────────────────────────────────────┐
│ LLMRouterChain                      │
│ • Analyzes: "sales", "total"       │
│ • Classifies: Numerical/tabular    │
│ • Decision: Route to CSV           │
│ • Returns: {"destination": "csv"}  │
└────────────┬────────────────────────┘
             │ Step 3: Execute CSV chain
             ▼
┌─────────────────────────────────────┐
│ CSV QA Chain                        │
│ • Receives query                    │
│ • Requests retrieval                │
└────────────┬────────────────────────┘
             │ Step 4: Retrieve docs
             ▼
┌─────────────────────────────────────┐
│ CSV Retriever                       │
│ • Embeds query                      │
│ • Similarity search                 │
│ • Returns top 10 matches            │
└────────────┬────────────────────────┘
             │ Step 5: Get vectors
             ▼
┌─────────────────────────────────────┐
│ CSV Vector Store                    │
│ • Searches embeddings               │
│ • Finds relevant rows               │
│ • Returns documents                 │
└────────────┬────────────────────────┘
             │ Step 6: Build context
             ▼
┌─────────────────────────────────────┐
│ Context Builder                     │
│ • Formats retrieved docs            │
│ • Creates prompt with context       │
│ • Adds original question            │
└────────────┬────────────────────────┘
             │ Step 7: LLM processing
             ▼
┌─────────────────────────────────────┐
│ ChatOpenAI (via OpenRouter)        │
│ • Receives: question + context      │
│ • Processes with GPT model          │
│ • Generates natural language answer │
└────────────┬────────────────────────┘
             │ Step 8: Return answer
             ▼
Answer: "The total sales for 2016 were..."
```

## 🏗️ Document Processing Pipeline

```
Document Files
    │
    ├─ *.pdf files
    │   │
    │   ▼
    │  PyPDFLoader
    │   │ • Extracts text per page
    │   │ • Preserves metadata
    │   │ • Creates Document objects
    │   ▼
    │  PDF Documents
    │   │ [metadata: {source, page, doc_type: 'pdf'}]
    │   ▼
    │  HuggingFace Embeddings
    │   │ • sentence-transformers/all-mpnet-base-v2
    │   │ • 768-dimensional vectors
    │   │ • Normalized for cosine similarity
    │   ▼
    │  PDF Vector Store
    │   │ • DocArrayInMemorySearch
    │   │ • Indexed embeddings
    │   │ • Fast similarity search
    │   ▼
    │  PDF Retriever (k=5)
    │
    ├─ *.docx files
    │   │
    │   ▼
    │  Docx2txtLoader
    │   │ • Extracts text content
    │   │ • Preserves structure
    │   │ • Creates Document objects
    │   ▼
    │  DOCX Documents
    │   │ [metadata: {source, doc_type: 'docx'}]
    │   ▼
    │  HuggingFace Embeddings
    │   │ • Same model as PDF
    │   │ • Consistent vector space
    │   ▼
    │  DOCX Vector Store
    │   │ • DocArrayInMemorySearch
    │   │ • Separate from PDF store
    │   ▼
    │  DOCX Retriever (k=5)
    │
    └─ *.csv files
        │
        ▼
       CSVLoader
        │ • Parses CSV rows
        │ • Each row = Document
        │ • Includes all columns
        ▼
       CSV Documents
        │ [metadata: {source, row, doc_type: 'csv'}]
        ▼
       HuggingFace Embeddings
        │ • Embeds row content
        │ • Captures relationships
        ▼
       CSV Vector Store
        │ • DocArrayInMemorySearch
        │ • Optimized for tabular data
        ▼
       CSV Retriever (k=10)
```

## 🧠 Router Decision Logic

```
                    User Query
                        │
                        ▼
            ┌──────────────────────┐
            │  Analyze Keywords    │
            │                      │
            │ • sales, orders,     │
            │   data, numbers?     │
            │   → CSV              │
            │                      │
            │ • report, findings,  │
            │   paper, study?      │
            │   → PDF              │
            │                      │
            │ • memo, letter,      │
            │   meeting, action?   │
            │   → DOCX             │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Analyze Intent      │
            │                      │
            │ • Numerical analysis?│
            │   → CSV              │
            │                      │
            │ • Summarization?     │
            │   → PDF/DOCX         │
            │                      │
            │ • Data query?        │
            │   → CSV              │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  LLM Classification  │
            │                      │
            │  Returns JSON:       │
            │  {                   │
            │    "destination":    │
            │      "pdf"|"docx"|   │
            │      "csv",          │
            │    "next_inputs":    │
            │      "original query"│
            │  }                   │
            └──────────┬───────────┘
                       │
                       ▼
              Route to Destination
```

## 📊 Data Structures

### Document Object
```python
Document(
    page_content: str,      # The actual text
    metadata: {
        'source': str,       # File path
        'doc_type': str,     # 'pdf', 'docx', or 'csv'
        'page': int,         # (PDF only) Page number
        'row': int           # (CSV only) Row number
    }
)
```

### Vector Store Structure
```
VectorStore
├─ documents: List[Document]
├─ embeddings: List[Vector[768]]
├─ index: SearchIndex
└─ metadata: Dict
```

### QA Chain Structure
```
RetrievalQA
├─ llm: ChatOpenAI
├─ retriever: VectorStoreRetriever
├─ chain_type: "stuff"
├─ return_source_documents: True
└─ verbose: True/False
```

## 🔀 Component Interaction Map

```
┌──────────────┐
│ User Layer   │
└──────┬───────┘
       │ query_documents() / query_specific_type()
       ▼
┌──────────────────────────┐
│ Application Layer        │
│ • MultiRouteChain        │◄──────┐
│ • LLMRouterChain         │       │
└──────┬───────────────────┘       │
       │                           │
       │ Routes to...              │
       ▼                           │
┌──────────────────────────┐       │
│ Chain Layer              │       │
│ • PDF QA Chain           │       │
│ • DOCX QA Chain          │       │ Feedback loop
│ • CSV QA Chain           │       │ for routing
└──────┬───────────────────┘       │ decisions
       │                           │
       │ Retrieves from...         │
       ▼                           │
┌──────────────────────────┐       │
│ Retrieval Layer          │       │
│ • PDF Retriever          │       │
│ • DOCX Retriever         │       │
│ • CSV Retriever          │       │
└──────┬───────────────────┘       │
       │                           │
       │ Searches in...            │
       ▼                           │
┌──────────────────────────┐       │
│ Vector Store Layer       │       │
│ • PDF VectorDB           │       │
│ • DOCX VectorDB          │       │
│ • CSV VectorDB           │       │
└──────┬───────────────────┘       │
       │                           │
       │ Contains...               │
       ▼                           │
┌──────────────────────────┐       │
│ Embedding Layer          │       │
│ HuggingFace Embeddings   │       │
│ (768-dim vectors)        │       │
└──────┬───────────────────┘       │
       │                           │
       │ Represents...             │
       ▼                           │
┌──────────────────────────┐       │
│ Data Layer               │       │
│ • PDF Documents          │       │
│ • DOCX Documents         │       │
│ • CSV Documents          │       │
└──────────────────────────┘       │
                                   │
       ┌───────────────────────────┘
       │
       ▼
┌──────────────────────────┐
│ LLM Layer                │
│ ChatOpenAI (OpenRouter)  │
│ • Routing decisions      │
│ • Answer generation      │
└──────────────────────────┘
```

## 🎯 Example: Complete Query Journey

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ INPUT: "What is the average sales amount in 2016?"     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                         │
                         ▼
        ┌────────────────────────────────┐
        │ Router Analysis                │
        │ Keywords: sales, amount, 2016  │
        │ Intent: Numerical calculation  │
        │ Decision: CSV                  │
        └────────────┬───────────────────┘
                     ▼
        ┌────────────────────────────────┐
        │ CSV QA Chain                   │
        │ Receives query + retriever     │
        └────────────┬───────────────────┘
                     ▼
        ┌────────────────────────────────┐
        │ CSV Retriever                  │
        │ Embeds query to 768-dim vector │
        │ Similarity search in CSV VectorDB│
        └────────────┬───────────────────┘
                     ▼
        ┌────────────────────────────────┐
        │ Returns Top 10 Relevant Rows   │
        │ • Row 5: Sales=261.96, 2016... │
        │ • Row 12: Sales=731.94, 2016...│
        │ • Row 23: Sales=14.62, 2016... │
        │ • ... (7 more rows)            │
        └────────────┬───────────────────┘
                     ▼
        ┌────────────────────────────────┐
        │ Build Context                  │
        │ Format: "Based on: [rows...]"  │
        └────────────┬───────────────────┘
                     ▼
        ┌────────────────────────────────┐
        │ LLM (ChatOpenAI)               │
        │ Prompt: Question + Context     │
        │ Process: Calculate average     │
        └────────────┬───────────────────┘
                     ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ OUTPUT: "The average sales amount in 2016 was $342.84, ┃
┃ calculated from 145 orders. The highest sale was       ┃
┃ $9,892.74 and the lowest was $2.99."                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## 📈 Scalability Model

```
Single Document Type (Before)
───────────────────────────
Documents: 1 file
Vector Store: 1 store
QA Chain: 1 chain
Complexity: O(1)


Multi-Document Type (After)
──────────────────────────
Documents: N files per type × 3 types
Vector Stores: 3 stores (isolated)
QA Chains: 3 chains
Router: 1 intelligent router
Complexity: O(3) = O(1) constant time
Routing Overhead: ~1-2 seconds per query


Extensible to:
─────────────
Documents: N files per type × M types
Vector Stores: M stores
QA Chains: M chains
Router: 1 router (handles M types)
Complexity: O(M) linear scaling
```

## 🔧 Configuration Points

```
┌─────────────────────────────────────────┐
│ Configuration Layer                     │
├─────────────────────────────────────────┤
│                                         │
│ ├─ Embeddings Model                    │
│ │  └─ sentence-transformers/all-mpnet │
│ │                                       │
│ ├─ LLM Model                           │
│ │  └─ openai/gpt-oss-20b:free         │
│ │                                       │
│ ├─ Retrieval Counts                    │
│ │  ├─ PDF: k=5                         │
│ │  ├─ DOCX: k=5                        │
│ │  └─ CSV: k=10                        │
│ │                                       │
│ ├─ Chain Type                          │
│ │  └─ "stuff" (alternatives: map_reduce)│
│ │                                       │
│ ├─ Directory                           │
│ │  └─ "." (current directory)          │
│ │                                       │
│ └─ Verbosity                           │
│    └─ True/False (debug output)        │
│                                         │
└─────────────────────────────────────────┘
```

---

**Legend:**
- `│` - Sequential flow
- `┌─┐` - Component boundary
- `◄──┐` - Feedback loop
- `┏━┓` - Input/Output
- `▼` - Data flow direction

