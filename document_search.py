"""
Multi-Document Search Engine
Automatically routes queries to PDF, DOCX, or CSV documents using LangChain
"""

import os
import glob
from typing import List, Dict
from dotenv import load_dotenv, find_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_community.document_loaders import CSVLoader, PyPDFLoader, Docx2txtLoader
from langchain.chains.router import MultiRetrievalQAChain
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables
_ = load_dotenv(find_dotenv())


class MultiDocumentSearchEngine:
    """
    A multi-document search engine that routes queries to appropriate document types
    """
    
    def __init__(self, directory: str = ".", model: str = "openai/gpt-oss-20b:free"):
        """
        Initialize the search engine
        
        Args:
            directory: Directory containing documents
            model: OpenRouter model name
        """
        self.directory = directory
        self.model = model
        
        # Initialize components
        print("Initializing embeddings...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            encode_kwargs={"normalize_embeddings": True},
        )
        
        print("Initializing LLM...")
        self.llm = ChatOpenAI(
            temperature=0.0,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model=model,
        )
        
        # Storage for documents and retriever infos
        self.all_documents = {}
        self.vector_stores = {}
        self.retrievers = {}
        self.retriever_infos = []
        self.router_qa_chain = None
        
    def load_documents(self) -> Dict[str, List[Document]]:
        """Load all documents from directory"""
        print(f"\nLoading documents from: {self.directory}")
        
        documents_by_type = {
            'pdf': [],
            'docx': [],
            'csv': []
        }
        
        # Load PDF files
        pdf_files = glob.glob(f"{self.directory}/*.pdf")
        for pdf_file in pdf_files:
            print(f"  Loading PDF: {pdf_file}")
            loader = PyPDFLoader(pdf_file)
            docs = loader.load()
            for doc in docs:
                doc.metadata['doc_type'] = 'pdf'
            documents_by_type['pdf'].extend(docs)
        
        # Load DOCX files
        docx_files = glob.glob(f"{self.directory}/*.docx")
        for docx_file in docx_files:
            print(f"  Loading DOCX: {docx_file}")
            loader = Docx2txtLoader(docx_file)
            docs = loader.load()
            for doc in docs:
                doc.metadata['doc_type'] = 'docx'
            documents_by_type['docx'].extend(docs)
        
        # Load CSV files
        csv_files = glob.glob(f"{self.directory}/*.csv")
        for csv_file in csv_files:
            print(f"  Loading CSV: {csv_file}")
            loader = CSVLoader(file_path=csv_file)
            docs = loader.load()
            for doc in docs:
                doc.metadata['doc_type'] = 'csv'
            documents_by_type['csv'].extend(docs)
        
        self.all_documents = documents_by_type
        
        print(f"\n=== Document Loading Summary ===")
        print(f"PDF documents: {len(documents_by_type['pdf'])}")
        print(f"DOCX documents: {len(documents_by_type['docx'])}")
        print(f"CSV documents: {len(documents_by_type['csv'])}")
        print(f"Total documents: {sum(len(docs) for docs in documents_by_type.values())}")
        
        return documents_by_type
    
    def create_vector_stores(self):
        """Create vector stores for each document type"""
        print("\nCreating vector stores...")
        
        if self.all_documents['pdf']:
            print("  Creating PDF vector store...")
            self.vector_stores['pdf'] = DocArrayInMemorySearch.from_documents(
                self.all_documents['pdf'], 
                self.embeddings
            )
            self.retrievers['pdf'] = self.vector_stores['pdf'].as_retriever(
                search_kwargs={"k": 5}
            )
        
        if self.all_documents['docx']:
            print("  Creating DOCX vector store...")
            self.vector_stores['docx'] = DocArrayInMemorySearch.from_documents(
                self.all_documents['docx'], 
                self.embeddings
            )
            self.retrievers['docx'] = self.vector_stores['docx'].as_retriever(
                search_kwargs={"k": 5}
            )
        
        if self.all_documents['csv']:
            print("  Creating CSV vector store...")
            self.vector_stores['csv'] = DocArrayInMemorySearch.from_documents(
                self.all_documents['csv'], 
                self.embeddings
            )
            self.retrievers['csv'] = self.vector_stores['csv'].as_retriever(
                search_kwargs={"k": 10}
            )
        
        print(f"Active retrievers: {list(self.retrievers.keys())}")
    
    def create_router(self):
        """Create the router chain using MultiRetrievalQAChain"""
        print("\nCreating router...")
        
        # Build retriever_infos for the router
        if 'pdf' in self.retrievers:
            self.retriever_infos.append({
                "name": "pdf",
                "description": "The pdf document is all about iphone, iphone 17 series launch. Good for answering questions about PDF documents, reports, articles, papers, documentation, manuals, and textual information stored in PDF format",
                "retriever": self.retrievers['pdf']
            })
        
        if 'docx' in self.retrievers:
            self.retriever_infos.append({
                "name": "docx",
                "description": "The word document is all about F1 Singapore Grand Prix 2025. Good for answering questions about Word documents, letters, memos, proposals, written content, formatted documents, and business documents stored in DOCX format",
                "retriever": self.retrievers['docx']
            })
        
        if 'csv' in self.retrievers:
            self.retriever_infos.append({
                "name": "csv",
                "description": "The csv document is all about sales data of a company. Good for answering questions about tabular data, spreadsheets, sales records, orders, numerical data, statistics, transactions, customer data, and structured data stored in CSV format",
                "retriever": self.retrievers['csv']
            })
        
        # Create MultiRetrievalQAChain
        self.router_qa_chain = MultiRetrievalQAChain.from_retrievers(
            llm=self.llm,
            retriever_infos=self.retriever_infos,
            default_chain_llm=self.llm,
            verbose=False
        )
        
        print("Router created successfully!")
        print(f"Available document types: {[info['name'] for info in self.retriever_infos]}")
    
    def initialize(self):
        """Initialize the entire search engine"""
        self.load_documents()
        self.create_vector_stores()
        self.create_router()
        print("\n✅ Search engine ready!\n")
    
    def query(self, user_query: str) -> str:
        """
        Query the search engine - router automatically picks the right document type
        
        Args:
            user_query: Your question (string)
            
        Returns:
            The answer
        """
        if not self.router_qa_chain:
            raise RuntimeError("Search engine not initialized. Call initialize() first.")
        
        print(f"\n{'='*60}")
        print(f"USER QUERY: {user_query}")
        print(f"{'='*60}\n")
        
        try:
            result = self.router_qa_chain.invoke({"input": user_query})
            
            # Extract answer from result
            if isinstance(result, str):
                answer = result
            elif isinstance(result, dict):
                answer = result.get("result") or result.get("output") or str(result)
            else:
                answer = str(result)
            
            print(f"\n{'='*60}")
            print("ANSWER:")
            print(f"{'='*60}")
            print(answer)
            print()
            
            return answer
            
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """Main function"""
    print("="*60)
    print("Multi-Document Search Engine")
    print("="*60)
    
    # Initialize search engine
    engine = MultiDocumentSearchEngine(directory=".")
    engine.initialize()
    
    # Interactive mode
    print("\n" + "="*60)
    print("Interactive Mode (type 'exit' to quit)")
    print("="*60)
    
    while True:
        try:
            question = input("\nYour question: ").strip()
            if question.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            if question:
                engine.query(question)
        except KeyboardInterrupt:
            print("\nbye!, see you soon!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
