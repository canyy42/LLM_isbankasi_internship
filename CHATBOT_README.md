# 🏦 Finans Asistanı Chatbot - Web Arayüzü

Bu proje, mevcut RAG pipeline'ınızı kullanarak güzel bir web arayüzü ile chatbot deneyimi sunar.

## ✨ Özellikler

- 🎨 **Modern ve Güzel Tasarım**: Profesyonel bankacılık teması
- 💬 **Gerçek Zamanlı Chat**: Anlık mesajlaşma deneyimi
- 🚀 **Hızlı Yanıt**: Groq API ile hızlı yanıt üretimi
- 📱 **Responsive Tasarım**: Mobil ve masaüstü uyumlu
- 🎯 **Önerilen Sorular**: Sık sorulan sorular için hızlı erişim
- ⌨️ **Klavye Kısayolları**: Enter ile gönder, Shift+Enter ile yeni satır
- 🌐 **Çok Dilli Destek**: Türkçe ve İngilizce otomatik algılama

## 🚀 Kurulum

### 1. Gereksinimler

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

`env.example` dosyasını `.env` olarak kopyalayın:

```bash
cp env.example .env
```

`.env` dosyasını düzenleyin:

```env
# Groq API Key (https://groq.com adresinden alın)
API_KEY=your_actual_groq_api_key_here

# Flask Secret Key (rastgele string)
SECRET_KEY=your_random_secret_key_here

# Flask Ayarları
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### 3. Veri Hazırlığı

Chatbot'un çalışması için aşağıdaki dosyaların mevcut olması gerekir:

```
data/
├── chunked_data.csv          # Chunk'lanmış veri
├── faiss_index.index         # FAISS index (opsiyonel)
└── faiss_metadata.pkl        # FAISS metadata (opsiyonel)
```

Eğer bu dosyalar yoksa, önce pipeline'ı çalıştırın:

```bash
bash scripts/run_pipeline.sh
```

## 🎯 Kullanım

### 1. Chatbot'u Başlatın

```bash
python app.py
```

### 2. Tarayıcıda Açın

```
http://localhost:5000
```

### 3. Sorularınızı Sorun

- Finans ve bankacılık ile ilgili herhangi bir soru sorabilirsiniz
- Önerilen sorular butonlarına tıklayarak hızlı başlayabilirsiniz
- Enter tuşu ile mesaj gönderin
- Shift+Enter ile yeni satır ekleyin

## 🎨 Arayüz Özellikleri

### Header
- Logo ve başlık
- Bağlantı durumu göstergesi
- Gerçek zamanlı sistem durumu

### Ana Alan
- Hoş geldin mesajı
- Önerilen sorular
- Chat geçmişi
- Yazıyor göstergesi

### Giriş Alanı
- Otomatik boyutlandırılan textarea
- Karakter sayacı (500 karakter limit)
- Gönder butonu
- Kullanım ipuçları

## ⌨️ Klavye Kısayolları

- **Enter**: Mesaj gönder
- **Shift + Enter**: Yeni satır ekle
- **Ctrl/Cmd + Enter**: Mesaj gönder (alternatif)
- **Escape**: Giriş alanını temizle

## 🔧 Geliştirme

### Dosya Yapısı

```
├── app.py                    # Flask ana uygulaması
├── templates/
│   └── index.html           # Ana HTML template
├── static/
│   ├── css/
│   │   └── style.css        # Stil dosyası
│   └── js/
│       └── chatbot.js       # JavaScript fonksiyonları
├── data/                    # Veri dosyaları
└── scripts/                 # Mevcut pipeline scriptleri
```

### Özelleştirme

#### CSS Stilleri
`static/css/style.css` dosyasında:
- Renk şeması
- Animasyonlar
- Responsive tasarım
- Font ve boyutlar

#### JavaScript Fonksiyonları
`static/js/chatbot.js` dosyasında:
- Chat mantığı
- API çağrıları
- UI etkileşimleri
- Hata yönetimi

#### HTML Template
`templates/index.html` dosyasında:
- Sayfa yapısı
- İçerik düzeni
- Önerilen sorular

## 🐛 Sorun Giderme

### Yaygın Hatalar

1. **"Bağlantı hatası" mesajı**
   - `.env` dosyasında `API_KEY` doğru mu?
   - Groq API anahtarınız geçerli mi?
   - İnternet bağlantınız var mı?

2. **"Veri yüklenemedi" hatası**
   - `data/chunked_data.csv` dosyası mevcut mu?
   - Pipeline çalıştırıldı mı?

3. **Port hatası**
   - Port 5000 başka bir uygulama tarafından kullanılıyor mu?
   - `.env` dosyasında farklı port belirtin

### Debug Modu

```bash
export FLASK_DEBUG=True
python app.py
```

## 📱 Mobil Uyumluluk

Chatbot tamamen responsive tasarlanmıştır:
- Mobil cihazlarda optimize edilmiş görünüm
- Touch-friendly butonlar
- Mobil tarayıcı uyumlu JavaScript

## 🔒 Güvenlik

- API anahtarları `.env` dosyasında saklanır
- Flask secret key ile session güvenliği
- Input validation ve sanitization
- CORS koruması

## 🚀 Production Deployment

### Gunicorn ile

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker ile

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📊 Performans

- Lazy loading ile hızlı başlangıç
- Optimized CSS ve JavaScript
- Efficient DOM manipulation
- Minimal API calls

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🆘 Destek

Sorunlarınız için:
1. GitHub Issues kullanın
2. README dosyasını kontrol edin
3. Debug modunda hata mesajlarını inceleyin

---

**Not**: Bu chatbot, mevcut RAG pipeline'ınızı kullanır. Pipeline'ın düzgün çalıştığından emin olun.
