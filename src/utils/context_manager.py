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
        # Increase number of results for better coverage
        relevant_docs = self.doc_processor.query_documents(query, n_results=5)
        
        if not relevant_docs:
            print("No relevant documents found")
            return ""
            
        # Improve context formatting
        context = "Here is relevant information from our knowledge base:\n\n"
        for i, doc in enumerate(relevant_docs, 1):
            # Add metadata for better context
            doc_type = doc['metadata'].get('type', 'general')
            category = doc['metadata'].get('category', 'general')
            context += f"{i}. [{doc_type}/{category}] {doc['content']}\n\n"
        
        print(f"Generated context: {context}")
        return context

    def enhance_prompt(self, query: str, system_prompt: str) -> str:
        """
        Enhance the system prompt with relevant context and instructions
        """
        context = self.get_context(query)
        if context:
            enhanced_prompt = f"""{system_prompt}

When answering questions, use the following context to provide accurate information. 
If the context contains relevant information, use it in your response.
If you're not sure about something, say so rather than making assumptions.

{context}

Please provide a clear, concise response based on the above context."""
            return enhanced_prompt
        return system_prompt 