# Multi-Document Search Engine - Quick Start Guide

## 🚀 Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
Create a `.env` file:
```
OPENROUTER_API_KEY=your_api_key_here
```

### 3. Add Your Documents
Place your files in the project directory:
- `*.pdf` - PDF documents
- `*.docx` - Word documents  
- `*.csv` - CSV/Excel files

### 4. Run the Notebook
Open `miniLM.ipynb` and run all cells.

## 📝 How to Query

### Basic Query (with Router)
The router automatically determines which document type to search:

```python
query_documents("Your question here")
```

**Examples:**
```python
# Will route to CSV
query_documents("What are the total sales?")

# Will route to PDF
query_documents("Summarize the report")

# Will route to DOCX
query_documents("What are the action items in the memo?")
```

### Direct Query (Advanced)
Query a specific document type directly:

```python
query_specific_type("Your question", "csv")   # Query CSV only
query_specific_type("Your question", "pdf")   # Query PDF only
query_specific_type("Your question", "docx")  # Query DOCX only
```

### Check Loaded Documents
```python
show_document_info()
```

## 🎯 Query Examples by Document Type

### CSV/Excel Queries
```python
query_documents("Which products have the highest profit margin?")
query_documents("List all transactions from 2016")
```

### PDF Queries
```python
query_documents("What are the main findings in the research paper?")
query_documents("Summarize the executive summary")
```

### Word Document Queries
```python
query_documents("Who own the Singapore Grand Prix 2025?")
query_documents("Explain the event of Singapore Grand Prix 2025")
query_documents("How qualifying day went in Singapore Grand Prix 2025?")
```

## 🔧 Router Behavior

The LangChain router analyzes your question and routes based on:

| Document Type | Routes When Query Contains... |
|--------------|-------------------------------|
| **CSV** | sales, orders, data, statistics, numbers, customers, transactions, revenue, profit |
| **PDF** | report, paper, document, findings, research, summary, analysis, study |
| **DOCX** | memo, letter, proposal, meeting, action items, stakeholders, deliverables |

## 🛠️ Advanced Features

### 1. Custom Document Directory
Change the directory to load documents from:

```python
# In Cell 5, modify:
all_documents = load_documents_by_type("./your_folder")
```

### 2. Adjust Retrieval Count
Modify how many document chunks to retrieve:

```python
# In Cell 6, change search_kwargs:
retriever = vector_store.as_retriever(search_kwargs={"k": 10})  # Get 10 chunks
```

### 3. Change LLM Model
```python
# In Cell 4, modify:
llm = ChatOpenAI(
    temperature=0.0,
    model="different/model:name",  # Change this
    # ... other params
)
```

### 4. Verbose Output
Control chain verbosity:

```python
# Set verbose=False to reduce output
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    verbose=False  # Change this
)
```

## 📊 Understanding the Output

When you run a query, you'll see:

1. **Router Decision** (if verbose=True)
   - Which document type was selected
   - Why it was selected

2. **Retrieval Process** (if verbose=True)
   - Documents being retrieved
   - Similarity scores

3. **Answer**
   - Generated response from the LLM

4. **Source Documents** (if enabled)
   - Which documents were used
   - Preview of relevant sections

## 🐛 Troubleshooting

### No documents loaded?
- Check that files are in the correct directory
- Verify file extensions (.pdf, .docx, .csv)
- Check console output for loading errors

### Router routing incorrectly?
- Be more specific in your query
- Use document type keywords
- Try `query_specific_type()` instead

### API errors?
- Verify your `.env` file exists
- Check API key is valid
- Ensure you have API credits

### Memory issues?
- Reduce the number of documents
- Lower the `k` value in retrievers
- Process documents in batches

## 💡 Best Practices

1. **Clear Questions**: Ask specific, well-formed questions
2. **Context**: Include relevant context in your query
3. **Document Organization**: Keep related documents together
4. **File Names**: Use descriptive file names
5. **Testing**: Test with simple queries first

## 🔄 Workflow Example

```python
# 1. Check what's loaded
show_document_info()

# 2. Start with a general query
query_documents("What information is available?")

# 3. Ask specific questions
query_documents("What were the total sales in Q1?")

# 4. Follow up
query_documents("Compare that to Q2")

# 5. Switch document types
query_documents("What does the report say about performance?")
```

## 📚 LangChain Components Used

- **Loaders**: `PyPDFLoader`, `Docx2txtLoader`, `CSVLoader`
- **Embeddings**: `HuggingFaceEmbeddings`
- **Vector Store**: `DocArrayInMemorySearch`
- **Chains**: `RetrievalQA`, `LLMRouterChain`, `MultiRouteChain`
- **LLM**: `ChatOpenAI` (via OpenRouter)

## 🤝 Contributing

Feel free to extend this system:
- Add new document types (JSON, XML, TXT)
- Implement document persistence
- Add more sophisticated routing logic
- Create a web interface
- Add document preprocessing

---

**Need Help?** Check the main README.md or the code comments in miniLM.ipynb

