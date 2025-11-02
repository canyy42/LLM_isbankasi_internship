#!/bin/bash

# Finans Asistanı Chatbot Başlatma Scripti
# Bu script chatbot'u başlatır ve gerekli kontrolleri yapar

echo "🏦 Finans Asistanı Chatbot Başlatılıyor..."
echo "=========================================="

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 bulunamadı. Lütfen Python3'ü yükleyin."
    exit 1
fi

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment oluşturuluyor..."
    python3 -m venv venv
fi

# Virtual environment'ı aktifleştir
echo "🔧 Virtual environment aktifleştiriliyor..."
source venv/bin/activate

# Gereksinimleri yükle
echo "📚 Gereksinimler yükleniyor..."
pip install -r requirements.txt

# .env dosyası kontrolü
if [ ! -f ".env" ]; then
    echo "⚠️  .env dosyası bulunamadı."
    echo "📝 env.example dosyasını .env olarak kopyalayın ve API anahtarınızı ekleyin."
    echo "   cp env.example .env"
    echo "   # .env dosyasını düzenleyin ve API_KEY ekleyin"
    exit 1
fi

# Veri dosyaları kontrolü
if [ ! -f "data/chunked_data.csv" ]; then
    echo "⚠️  Veri dosyaları bulunamadı."
    echo "📊 Pipeline'ı çalıştırmak ister misiniz? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🚀 Pipeline çalıştırılıyor..."
        bash scripts/run_pipeline.sh
    else
        echo "❌ Veri dosyaları olmadan chatbot çalışamaz."
        exit 1
    fi
fi

# Chatbot'u başlat
echo "🚀 Chatbot başlatılıyor..."
echo "🌐 Tarayıcıda http://localhost:5000 adresini açın"
echo "⏹️  Durdurmak için Ctrl+C tuşlayın"
echo ""

python app.py
