# scripts/rag.py

#!/usr/bin/env python3

"""
rag.py

Amaç:
- RAG (Retrieval-Augmented Generation) işlevlerini sağla
- Prompt oluştur
- Groq ChatCompletion ile yanıt üret
- FAISS ile vektör arama yap
"""

import faiss
import numpy as np
from dotenv import load_dotenv
import os
from groq import Groq
import pandas as pd
from langdetect import detect
import pickle

print("RAG sistemi başlatılıyor...")

load_dotenv()

api_key = os.getenv("API_KEY")
client = Groq(api_key=api_key)

# Load data
try:
    df = pd.read_csv("data/chunked_data.csv")
    chunked_data = df.to_dict(orient="records")
    
    # Load FAISS index if available
    if os.path.exists("data/faiss_index.index"):
        index = faiss.read_index("data/faiss_index.index")
        with open("data/faiss_metadata.pkl", "rb") as f:
            metadata = pickle.load(f)
    else:
        index = None
        metadata = None
        print("⚠️  FAISS index bulunamadı, basit arama kullanılıyor")
except Exception as e:
    print(f"❌ Veri yükleme hatası: {e}")
    chunked_data = []
    index = None
    metadata = None

def search_context(question, top_k=3):
    """Search for relevant context using FAISS or fallback to simple search"""
    if index is not None and metadata is not None:
        # Use FAISS for fast similarity search
        try:
            # For now, we'll use a simple approach
            # In a real implementation, you'd embed the question and search
            relevant_chunks = []
            question_lower = question.lower()
            
            for chunk in chunked_data[:10]:  # Search in first 10 chunks for demo
                if any(word in chunk.get('content', '').lower() for word in question_lower.split()):
                    relevant_chunks.append(chunk.get('content', '')[:500])
                    if len(relevant_chunks) >= top_k:
                        break
            
            return "\n\n".join(relevant_chunks) if relevant_chunks else "Finans ve bankacılık alanında genel bilgiler."
        except Exception as e:
            print(f"FAISS search error: {e}")
    
    # Fallback to simple search
    relevant_chunks = []
    question_lower = question.lower()
    
    for chunk in chunked_data[:20]:
        if any(word in chunk.get('content', '').lower() for word in question_lower.split()):
            relevant_chunks.append(chunk.get('content', '')[:500])
            if len(relevant_chunks) >= top_k:
                break
    
    return "\n\n".join(relevant_chunks) if relevant_chunks else "Finans ve bankacılık alanında genel bilgiler."

def generate_answer(question, conversation_history=None):
    """Generate answer using Groq API with RAG context"""
    try:
        context = search_context(question)
        
        # Detect language with character length check first
        try:
            if len(question) < 12:
                lang_text = "Türkçe"
            elif detect(question) == "tr":
                lang_text = "Türkçe"
            elif detect(question) == "en":
                lang_text = "İngilizce"
            else:
                lang_text = "Türkçe"
        except:
            lang_text = "Türkçe"
        
        # Generate conversation summary if history exists
        conversation_summary = ""
        if conversation_history and len(conversation_history) > 0:
            try:
                summary_prompt = f"""
Aşağıdaki konuşma geçmişini kısa bir özet haline getir. 
Sadece önemli noktaları ve konu bağlamını belirt:

{conversation_history}

Özet:"""
                
                summary_response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": "Sen bir konuşma özetleyicisisin. Sadece önemli noktaları kısaca özetle."},
                        {"role": "user", "content": summary_prompt}
                    ],
                    max_tokens=150
                )
                conversation_summary = summary_response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Conversation summary error: {e}")
                conversation_summary = ""

        # Main prompt with context and conversation history
        prompt = f"""
Sen finans, bankacılık ve ekonomi alanlarında uzmanlaşmış bir yapay zekâ danışmanısın.
Aşağıda bir kullanıcının sorusu ve bu soruya dair bazı bilgi parçaları (bağlam) yer alıyor. 
Görevin, bu bağlama dayanarak doğru, açık ve tekrar etmeyen bir cevap üretmek.

❗️ Cevabını hazırlarken şu kurallara dikkat et:
- Aynı kelimeleri tekrar tekrar kullanma. Anlamı koruyarak eş anlamlılarla zenginleştir.
- Gereksiz tekrarlar, döngüsel anlatımlar ve soyut genellemelerden kaçın.
- Uzunsa madde madde yaz.
- Elindeki bilgi yetersizse bunu dürüstçe belirt.
- Üst üste aynı kelimeleri kullanma.

### CEVAP DİLİ ###
{lang_text}

### KONUŞMA GEÇMİŞİ ###
{conversation_summary if conversation_summary else "Yeni konuşma"}

### BAĞLAM ###
{context}

### SORU ###
{question}

### CEVAP ###
"""

        response = client.chat.completions.create(
            model="llama3-70b-8192",  # veya llama3-8b-8192
            messages=[
                {"role": "system", "content": "Sen bir finans asistanısın. Soruları açık, anlaşılır ve bağlama dayalı olarak cevapla."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"[!] Yanıt üretme hatası: {e}"

def main():
    """
    Bankacılık asistanı için interaktif komut satırı uygulaması.
    Her soruyu ayrı işlem olarak işler, geçmişi hatırlamaz.
    """
    print("🏦 Finans Asistanı RAG Sistemi")
    print("=" * 40)
    
    while True:
        question = input("\n💬 Soru (çıkmak için 'q'): ").strip()
        if question.lower() in ["q", "-quit", "çık", "exit", "dur", "du", "d"]:
            print("🔚 Çıkılıyor...")
            break
        
        if not question:
            continue
            
        print("🔍 Bağlam aranıyor...")
        answer = generate_answer(question)
        print("\n📌 Yanıt:")
        print(answer)
        print("-" * 50)

if __name__ == "__main__":
    main()
