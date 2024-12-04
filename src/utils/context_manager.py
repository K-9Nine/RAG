from .document_processor import DocumentProcessor
from typing import List, Dict

class ContextManager:
    def __init__(self, doc_processor: DocumentProcessor):
        self.doc_processor = doc_processor

    def get_context(self, query: str) -> str:
        """
        Get relevant context for a query
        """
        print(f"Getting context for query: {query}")
        relevant_docs = self.doc_processor.query_documents(query)
        
        if not relevant_docs:
            print("No relevant documents found")
            return ""
            
        context = "Relevant information from our knowledge base:\n\n"
        for doc in relevant_docs:
            context += f"- {doc['content']}\n"
        
        print(f"Generated context: {context}")
        return context

    def enhance_prompt(self, query: str, system_prompt: str) -> str:
        """
        Enhance the system prompt with relevant context
        """
        context = self.get_context(query)
        if context:
            enhanced_prompt = f"{system_prompt}\n\nContext:\n{context}"
            return enhanced_prompt
        return system_prompt 