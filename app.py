from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
from groq import Groq
import pandas as pd
from langdetect import detect
import faiss
import numpy as np
import json
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize Groq client
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
            import pickle
            metadata = pickle.load(f)
    else:
        index = None
        metadata = None
except Exception as e:
    print(f"Data loading error: {e}")
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
    """Generate answer using Groq API"""
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

ÖZET:"""
                summary_response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": "Sen bir konuşma özetleyicisisin. Kısa ve öz özet yap."},
                        {"role": "user", "content": summary_prompt}
                    ],
                    max_tokens=200,
                    temperature=0.3
                )
                conversation_summary = summary_response.choices[0].message.content.strip()
            except Exception as e:
                conversation_summary = "Konuşma geçmişi yüklenemedi."
        
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
- Kullanıcıya yardımcı olacak pratik bilgiler ver.
- Önceki konuşma geçmişini dikkate al ve tutarlı cevaplar ver.

### DİL ###
{lang_text}

### KONUŞMA GEÇMİŞİ ###
{conversation_summary}

### BAĞLAM ###
{context}

### SORU ###
{question}

### CEVAP ###
"""

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Sen bir finans asistanısın. Soruları açık, anlaşılır ve bağlama dayalı olarak cevapla. Türkçe sorulara Türkçe, İngilizce sorulara İngilizce cevap ver."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Üzgünüm, yanıt üretirken bir hata oluştu: {str(e)}"

@app.route('/')
def index():
    """Main chatbot interface"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Mesaj boş olamaz'}), 400
        

        
        # Get conversation history from session (last 10 messages = 5 pairs)
        if 'conversation_history' not in session:
            session['conversation_history'] = []
        
        conversation_history = session['conversation_history']
        
        # Generate response with conversation history
        response = generate_answer(message, conversation_history)
        
        # Add new message pair to history
        conversation_history.append(f"Kullanıcı: {message}")
        conversation_history.append(f"Asistan: {response}")
        
        # Keep only last 10 messages (5 pairs)
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        # Update session
        session['conversation_history'] = conversation_history
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Bir hata oluştu: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'data_loaded': len(chunked_data) > 0,
        'faiss_available': index is not None,
        'groq_configured': bool(api_key)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
