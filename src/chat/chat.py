from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from deep_translator import GoogleTranslator
from langdetect import detect  
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.retrieval.retriever import load_retriever
from src.llm.model import load_llm

# Stronger multilingual prompt
ANSWER_PROMPT = """
You are a knowledgeable herbal medicine expert.
Use ONLY the context below to answer the question.

Context:
{context}

Question: {question}

CRITICAL LANGUAGE INSTRUCTION:
The question was asked in {language}.
You MUST respond ENTIRELY in {language}.
Do NOT mix languages.
Every word of your answer must be in {language}.

If the context doesn't contain the answer, say in {language}: "I don't have that information."

Your complete answer in {language}:
"""

def detect_language(text):
    """Detect input language"""
    try:
        lang_code = detect(text)
        
        # Map language codes to names
        lang_map = {
            'el': 'Greek',
            'en': 'English', 
            'pl': 'Polish',
            'sl': 'Slovenian',
            'es': 'Spanish',
            'de': 'German',
            'fr': 'French',
            'it': 'Italian',
            'tr': 'Turkish',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'ru': 'Russian',
        }
        
        language_name = lang_map.get(lang_code, 'English')
        return language_name, lang_code
    except:
        return 'English', 'en'

def format_docs(docs):
    """Format retrieved documents"""
    return "\n\n".join(doc.page_content for doc in docs)

def build_chain():
    prompt = PromptTemplate(
        template=ANSWER_PROMPT,
        input_variables=["context", "question", "language"]
    )
    retriever = load_retriever()
    llm = load_llm()

    def pipeline(question):
        # 1. Detect original language
        language_name, lang_code = detect_language(question)
        
        # 2. Translate to English for retrieval (if needed)
        if lang_code != 'en':
            try:
                english_question = GoogleTranslator(
                    source=lang_code, 
                    target='en'
                ).translate(question)
            except Exception as e:
                print(f"Translation error: {e}")
                english_question = question
        else:
            english_question = question
        
        # 3. Retrieve documents using English query
        docs = retriever.invoke(english_question)
        context = format_docs(docs)
        
        # 4. Generate answer in original language
        answer = (prompt | llm | StrOutputParser()).invoke({
            "context": context,
            "question": question,
            "language": language_name
        })
        
        return answer

    return RunnableLambda(pipeline)

def chat():
    print("Herbal Assistant ready. Type 'exit' to quit.\n")
    chain = build_chain()
    
    while True:
        question = input("You: ").strip()
        if question.lower() == "exit":
            break
        if not question:
            continue
        
        answer = chain.invoke(question)
        print(f"\nAssistant: {answer}\n")

if __name__ == "__main__":
    chat()