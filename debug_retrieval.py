"""
Simple script to see what your chatbot is finding when you ask questions.
Run this to diagnose retrieval issues WITHOUT changing any existing code.
"""

from src.retrieval.retriever import load_retriever

def debug_query(question):
    """Show what documents the chatbot finds for a question"""
    
    print("\n" + "="*60)
    print(f"QUESTION: {question}")
    print("="*60)
    
    # Load retriever
    retriever = load_retriever()
    
    # Try to detect if Greek and translate
    try:
        from src.ingest.translator import translate_to_english, is_greek
        if is_greek(question):
            english_query = translate_to_english(question)
            print(f"\nTranslated to: {english_query}")
        else:
            english_query = question
    except ImportError:
        print("\nUsing original query (translation functions not found)")
        english_query = question
    
    # Get documents - try different method names
    try:
        docs = retriever.invoke(english_query)  # Newer LangChain versions
    except AttributeError:
        try:
            docs = retriever._get_relevant_documents(english_query)  # Older versions
        except:
            docs = retriever.get_relevant_documents(english_query)
    
    print(f"\n📚 FOUND {len(docs)} DOCUMENTS:\n")
    
    # Show each document
    for i, doc in enumerate(docs, 1):
        print(f"\n--- Document {i} ---")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"\nGreek Text Preview:")
        print(doc.page_content[:300] + "...")
        print("-" * 60)
    
    print("\n✅ Done! Review the documents above to see if they contain the answer.\n")


if __name__ == "__main__":
    # Test with your problematic questions
    test_questions = [
        "Ποιες είναι οι ιδιότητες του χαμομηλιού;",  # ✅ This worked!
        "Τι βότανο βοηθάει στον ύπνο;",
        
        # ADD YOUR ACTUAL PROBLEM QUESTIONS HERE:
        # (Questions where the chatbot gives WRONG answers)
        # "Ποιες είναι οι ιδιότητες της λεβάντας;",
        # "Πώς χρησιμοποιώ το μελισσόχορτο;",
        # etc.
    ]
    
    for question in test_questions:
        debug_query(question)
        input("\nPress Enter to test next question...")