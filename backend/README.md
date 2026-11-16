# Nur Mizan API
Render'da bu deponun render.yaml Blueprint dosyasıyla dağıtın.
Gizli değişkenler: OPENAI_API_KEY (OpenAI platformundan), APP_ACCESS_TOKEN (uzun rastgele erişim kodu).
Bu erişim kodunu herkese açık paylaşmayın. Kullanıcı sayısı artınca gerçek kimlik doğrulama, hız sınırı ve maliyet kotası ekleyin.
GET /health servis durumunu gösterir. POST /ask JSON {"question":"..."} ve X-App-Access başlığı bekler.
sources.json varsayılan olarak boş. Kaynak eklemek için lisans/izin, alıntı doğrulama ve editör kontrolü gerekir.
Bu ilk sürümde anlamsal arama değil basit kelime eşleştirmesi vardır.