from .document_processor import DocumentProcessor
from .context_manager import ContextManager

def test_query():
    processor = DocumentProcessor()
    context_manager = ContextManager(processor)
    
    test_queries = [
        "what is callswitch one",
        "how do I set up call recording",
        "explain the mobile app features"
    ]
    
    for query in test_queries:
        print(f"\n\nTesting query: {query}")
        print("=" * 50)
        
        # Test direct document retrieval
        print("\nDirect Document Results:")
        results = processor.query_documents(query, n_results=5)
        for i, doc in enumerate(results, 1):
            print(f"\nDocument {i}:")
            print(f"Content: {doc['content']}")
            print(f"Metadata: {doc['metadata']}")
        
        # Test context generation
        print("\nGenerated Context:")
        context = context_manager.get_context(query)
        print(context)
        
        # Test full prompt enhancement
        print("\nEnhanced Prompt:")
        system_prompt = "You are an IT Support Assistant."
        enhanced_prompt = context_manager.enhance_prompt(query, system_prompt)
        print(enhanced_prompt)

if __name__ == "__main__":
    test_query() 