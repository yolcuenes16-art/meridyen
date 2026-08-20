# Meridyen Backend

Çalışan, mahremiyet-öncelikli Türkçe sosyal yapay zekâ API'si. Bu paket mevcut uygulamadan bağımsızdır; FastAPI ile doğrudan ayağa kalkar.

## Çalıştırma

```powershell
cd meridyen_backend
..\.venv\Scripts\python -m pip install -e ".[test]"
..\.venv\Scripts\python -m uvicorn meridyen.main:app --app-dir src --reload
```

API dokümantasyonu: `http://localhost:8000/docs`. Test: `..\.venv\Scripts\python -m pytest`.

## Karar çekirdeği

Metin tek geçişte altı çok-görevli sinyal üretir: duygu, toksisite, spam, Odak, Öğrenme ve Eğlence uyumu. `MultiTaskInference`, ONNX model yolu verildiğinde ONNX Runtime oturumunu başlatır; model dağıtımı olmadan aynı API sözleşmesini koruyan Türkçe güvenlik-temelli yerel sınıflandırıcıyı kullanır. LoRA eğitimi `meridyen.train_lora` ile yapılır; eğitim verisindeki her satır altı hedefi içermelidir.

Skorlar yalnızca içerik metni ve içerik üreticisinin açık katılım tercihi ile belirlenir. Kullanıcı ruh hâli çıkarılmaz; kullanım modu açık rıza ile seçilir.

- `Ws = 100 σ(1.65s + 1.15m - 2.8t - 1.9p)`
- `Rw = 100(.44Ws + .24M + .14Q + .10N + .08E)(.65 + .35e^(-age/36))`
- `Vm = clip(.7 + .9Ws + .3Q - .4 log(1+followers)/log(1e6), .5, 1.6)`

Burada tüm büyük harfli girişler 0-1 aralığına normalize edilir. `Ws`: refah, `M`: seçilen moda uygunluk, `Q`: güvenilir kalite, `N`: yenilik, `E`: etkileşimdir. Toksik veya spam içeriği ödül ve görünürlükten kesin olarak dışlanır.

## Güvenlik ve mahremiyet

- Rıza kaydı yoksa kullanıcı modu saklanmaz; rıza iptali kaydı siler.
- Toplu metrik API'si kimlik ya da ham içerik kabul etmez; iki taraflı geometrik diferansiyel gizlilik mekanizması uygular.
- Docker imajı ayrıcalıksız kullanıcı ile çalışır; compose profili salt-okunur dosya sistemi, tüm Linux yeteneklerinin kaldırılması ve `no-new-privileges` kullanır.
- Yüksek riskli toksisite/spam içeriği gelir dağıtımına katılamaz.
