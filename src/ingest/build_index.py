from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from deep_translator import GoogleTranslator
import sys, os
import time
 
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
 
from src.config import RAW_PDFS_DIR, VECTOR_STORE_DIR, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
from src.ingest.translator import is_greek
 
 
BOILERPLATE_PHRASES = [
    "αποξηραμένα βότανα μπορούν να αποθηκευτούν",
    "ξήρανση των βοτάνων σε πολύ υψηλή θερμοκρασία",
    "γεύση προέρχεται από έλαια στα κυτταρικά τοιχώματα",
    "Consultation with a specialist is considered necessary",
    "information provided has been drawn from academic books",
]
 
 
def is_boilerplate(text):
    return any(phrase.lower() in text.lower() for phrase in BOILERPLATE_PHRASES)
 
 
def translate_chunk(text):
    """Translate Greek text to English with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if len(text) <= 4500:
                return GoogleTranslator(source='el', target='en').translate(text)
            
            # Handle long text by splitting into parts
            parts = []
            words = text.split()
            current = ""
            for word in words:
                if len(current) + len(word) + 1 < 4500:
                    current += " " + word
                else:
                    parts.append(GoogleTranslator(source='el', target='en').translate(current.strip()))
                    current = word
                    time.sleep(0.1)  # Rate limiting between parts
            if current:
                parts.append(GoogleTranslator(source='el', target='en').translate(current.strip()))
            return " ".join(parts)
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  ⚠️  Translation attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
            else:
                print(f"  ❌ Translation failed after {max_retries} attempts: {e}")
                return text  # Fallback to original
 
 
def load_documents():
    """Load PDFs and DOCX files recursively from all subfolders."""
    documents = []
 
    # Load PDFs recursively
    print(f"  📂 Scanning for PDFs in: {RAW_PDFS_DIR}")
    pdf_loader = PyPDFDirectoryLoader(str(RAW_PDFS_DIR), recursive=True)
    pdf_docs = pdf_loader.load()
    print(f"  📄 PDFs: {len(pdf_docs)} pages loaded.")
    documents.extend(pdf_docs)
 
    # Load DOCX files recursively - FIXED!
    print(f"  📂 Scanning for DOCX files in all subfolders...")
    docx_loader = DirectoryLoader(
        str(RAW_PDFS_DIR),
        glob="**/*.docx",
        loader_cls=Docx2txtLoader,
        recursive=True  # ← THIS WAS MISSING!
    )
    docx_docs = docx_loader.load()
    print(f"  📝 DOCX: {len(docx_docs)} documents loaded.")
    documents.extend(docx_docs)
 
    return documents
 
 
def build_index(test_mode=False):
    print("=" * 70)
    print("🌿 HEALTH & WELLNESS RAG - INDEX BUILDER")
    print("=" * 70)
    
    print("\n📂 Loading documents...")
    documents = load_documents()
 
    if not documents:
        print("❌ No documents found.")
        return
 
    # In test mode only process first 5 documents for faster testing
    if test_mode:
        documents = documents[:5]
        print(f"\n🧪 TEST MODE: Processing first 5 documents only.")
        print(f"   (This will create ~30-50 chunks for quick validation)")
    
    print(f"\n📊 Total: {len(documents)} documents loaded.")
 
    print("\n✂️  Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)
    print(f"   Created {len(chunks)} chunks.")
 
    # Remove boilerplate
    print("\n🧹 Removing boilerplate...")
    chunks = [c for c in chunks if not is_boilerplate(c.page_content)]
    print(f"   {len(chunks)} chunks remaining after cleanup.")
 
    # Translate Greek chunks to English
    print("\n🔄 Translating chunks to English...")
    print(f"   (This may take a while - ~0.5s per chunk)")
    
    translated_chunks = []
    greek_count = 0
    english_count = 0
    
    start_time = time.time()
    
    for i, chunk in enumerate(chunks):
        if is_greek(chunk.page_content):
            translated = translate_chunk(chunk.page_content)
            translated_chunks.append(Document(
                page_content=translated,
                metadata={**chunk.metadata, "language": "en", "translated": True}
            ))
            greek_count += 1
            
            # Progress indicator every 10 chunks
            if (i + 1) % 10 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / (i + 1)
                remaining = (len(chunks) - i - 1) * avg_time
                print(f"   [{i+1}/{len(chunks)}] Translated (ETA: {remaining/60:.1f} min)")
            
            time.sleep(0.2)  # Rate limiting to avoid Google Translate issues
        else:
            # Already English, keep as is
            translated_chunks.append(Document(
                page_content=chunk.page_content,
                metadata={**chunk.metadata, "language": "en"}
            ))
            english_count += 1
 
    print(f"\n✅ Translation complete!")
    print(f"   Greek chunks translated: {greek_count}")
    print(f"   English chunks kept: {english_count}")
    print(f"   Total chunks in index: {len(translated_chunks)}")
 
    print("\n🔢 Generating embeddings...")
    print(f"   Model: {EMBEDDING_MODEL}")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vector_store = FAISS.from_documents(translated_chunks, embeddings)
 
    print("\n💾 Saving vector store...")
    vector_store.save_local(str(VECTOR_STORE_DIR))
    
    total_time = time.time() - start_time
    print(f"\n{'=' * 70}")
    print(f"✅ DONE! Index saved to {VECTOR_STORE_DIR}")
    print(f"   Total time: {total_time/60:.1f} minutes")
    print(f"{'=' * 70}\n")
 
 
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Build FAISS index with English translation for Greek health and wellness documents"
    )
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Run in test mode with 5 documents (~30-50 chunks, ~5-10 minutes)"
    )
    args = parser.parse_args()
    
    build_index(test_mode=args.test)