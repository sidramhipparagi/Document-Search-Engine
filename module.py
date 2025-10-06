#Import as a module
from document_search import MultiDocumentSearchEngine

engine = MultiDocumentSearchEngine(directory=".")
engine.initialize()

# Ask your question here:
engine.query("What are the iPhone 17 colors?")