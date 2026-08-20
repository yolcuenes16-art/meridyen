"""Meridyen ML Training Pipeline.

Turkish multi-task text classification:
  - Toxicity detection
  - Spam detection  
  - Sentiment analysis (positive/negative)
  - Mode fit (focus / learning / fun)

Uses TF-IDF features + Logistic Regression, exported to ONNX.
"""

import json
import random
from pathlib import Path

import numpy as np
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer

random.seed(42)
np.random.seed(42)

# ── Synthetic Turkish Training Data ──────────────────────────────────────

TOXIC_DATA = [
    ("Sen çok aptalsın, hiçbir şey bilmiyonsun", {"toxic": True, "sentiment_neg": True}),
    ("Allah belanı versin, seni sevmiyorum", {"toxic": True, "sentiment_neg": True}),
    ("Bu enayiler hâlâ inanıyor mu bunlara", {"toxic": True, "sentiment_neg": True}),
    ("Salak mısın sen, okumuyor musun", {"toxic": True, "sentiment_neg": True}),
    ("İnsanları kandırmaya utanmıyor musun", {"toxic": True, "sentiment_neg": True}),
    ("Nefret dolu birisin, uzak dur benden", {"toxic": True, "sentiment_neg": True}),
    ("Böyleleriniigramdan atarım", {"toxic": True, "sentiment_neg": True}),
    ("Senin gibi gerizekalılar yüzünden ülke batıyor", {"toxic": True, "sentiment_neg": True}),
    ("Kahpe liseli, sus artık", {"toxic": True, "sentiment_neg": True}),
    ("Ezik herif, hayatın boyunca bir şey başaramayacaksın", {"toxic": True, "sentiment_neg": True}),
    ("Orospu çocukları, hepsi yalan söylüyor", {"toxic": True, "sentiment_neg": True}),
    ("Piç kurusu, seni iteration ever ederim", {"toxic": True, "sentiment_neg": True}),
    ("Ananı sikeyim senin, ne konuşuyorsun", {"toxic": True, "sentiment_neg": True}),
    ("Yarrak kafalı, bir de utanmadan yazıyorsun", {"toxic": True, "sentiment_neg": True}),
    ("Göt lalesi, kapat şunu", {"toxic": True, "sentiment_neg": True}),
    ("İbne misin sen, niye böyle yapıyorsun", {"toxic": True, "sentiment_neg": True}),
    ("Amk salağı, oku da öğren", {"toxic": True, "sentiment_neg": True}),
    ("Aq çocukları, dolandırıcılık yapıyorlar", {"toxic": True, "sentiment_neg": True}),
    ("Ne Mal adamsın be, her şeyi batırıyorsun", {"toxic": True, "sentiment_neg": True}),
    ("Pezevenk, seni kimse sevmiyor zaten", {"toxic": True, "sentiment_neg": True}),
    ("Öldürmek lazım bunları, hiçbir işe yaramıyorlar", {"toxic": True, "sentiment_neg": True}),
    ("Şiddetle çözüm buluruz biz, sus sen", {"toxic": True, "sentiment_neg": True}),
    ("Seni gebertirim ha, konuşma así", {"toxic": True, "sentiment_neg": True}),
    ("Hakaret etmek zorunda mıyım, sen beni çıldırtıyorsun", {"toxic": True, "sentiment_neg": True}),
    ("Aşağılık herif, senin gibi insanlara tahammülüm yok", {"toxic": True, "sentiment_neg": True}),
    ("Irkçı pratikler sergiliyorsun, yazık sana", {"toxic": True, "sentiment_neg": True}),
    ("Bu tehditleri ciddiye alıyorum, polisi arayacağım", {"toxic": True, "sentiment_neg": True}),
    ("Irkcı bir topluluk burası, hep kırıyorlar", {"toxic": True, "sentiment_neg": True}),
    ("Bana Defol git, burada istenmiyorsun", {"toxic": True, "sentiment_neg": True}),
    ("Senin gibiler yüzünden nefret ediyorum burdan", {"toxic": True, "sentiment_neg": True}),
]

CLEAN_DATA = [
    ("Bugün hava çok güzel, yürüyüşe çıktım", {"toxic": False, "sentiment_pos": True}),
    ("Yeni bir kitap okumaya başladım, çok güzel", {"toxic": False, "sentiment_pos": True}),
    ("Arkadaşımla kahve içtik, sohbet ettik", {"toxic": False, "sentiment_pos": True}),
    ("Bu makaleyi herkesin okumasını tavsiye ederim", {"toxic": False, "sentiment_pos": True}),
    ("Sabah sporu yapınca günüm çok iyi geçiyor", {"toxic": False, "sentiment_pos": True}),
    ("Yeni bir hobi edindim, resim yapıyorum artık", {"toxic": False, "sentiment_pos": True}),
    ("Çok güzel bir film izledim dün gece", {"toxic": False, "sentiment_pos": True}),
    ("Ailemle vakit geçirmek en güzel şey", {"toxic": False, "sentiment_pos": True}),
    ("Bu restoranı şiddetle tavsiye ederim", {"toxic": False, "sentiment_pos": True}),
    ("Bugün çok verimli bir gün geçirdim", {"toxic": False, "sentiment_pos": True}),
    ("Yeni şeyler öğrenmek her zaman iyi hissettirir", {"toxic": False, "sentiment_pos": True}),
    ("Müzik dinlemek ruh halimi düzeltiyor", {"toxic": False, "sentiment_pos": True}),
    ("Doğada vakit geçirmek insana huzur verir", {"toxic": False, "sentiment_pos": True}),
    ("Bu projede çok emek var, tebrikler", {"toxic": False, "sentiment_pos": True}),
    ("Kendime yeni hedefler koydum, başlıyorum", {"toxic": False, "sentiment_pos": True}),
    ("Bugün bir şey öğrendim, paylaşmak istedim", {"toxic": False, "sentiment_pos": True}),
    ("Bu konuda çok araştırma yaptım, bilgi paylaşıyorum", {"toxic": False, "sentiment_pos": True}),
    ("Sakin olmak için nefes egzersizleri yapıyorum", {"toxic": False, "sentiment_pos": True}),
    ("Başarıya giden yol sabır ve çalışmadan geçer", {"toxic": False, "sentiment_pos": True}),
    ("Umudunuzu kaybetmeyin, her gün yeni bir başlangıç", {"toxic": False, "sentiment_pos": True}),
    ("Bu topluluk çok destekleyici, teşekkür ederim", {"toxic": False, "sentiment_pos": True}),
    ("Küçük adımlar büyük değişikliklere yol açar", {"toxic": False, "sentiment_pos": True}),
    ("Bugün en sevdiğim yemeği pişirdim", {"toxic": False, "sentiment_pos": True}),
    ("Yürüyüş yapmak zihni temizliyor", {"toxic": False, "sentiment_pos": True}),
    ("Bu bilgiyi useful buldum, kaydettim", {"toxic": False, "sentiment_pos": True}),
    ("Sabah erken kalkmak günün verimliliğini artırıyor", {"toxic": False, "sentiment_pos": True}),
    ("Bu paylaşım için teşekkürler, çok faydalı", {"toxic": False, "sentiment_pos": True}),
    ("Kendini geliştirmek bitmeyen bir yolculuk", {"toxic": False, "sentiment_pos": True}),
    ("Güzel bir gün olsun herkese", {"toxic": False, "sentiment_pos": True}),
    ("İyi geceler, yarın yeni umutlarla uyanacağız", {"toxic": False, "sentiment_pos": True}),
    ("Hava biraz soğuk ama güzel", {"toxic": False}),
    ("Bu konuyu araştırıyorum, ilginç bulgular var", {"toxic": False}),
    ("Akşam yürüyüşü yaptım, çok rahatladım", {"toxic": False}),
    ("Yeni bir şeyler denemek her zaman heyecan verici", {"toxic": False}),
    ("Bu blog yazısını okudum, tavsiye ederim", {"toxic": False}),
    ("Derin çalışma tekniklerini uygulamaya başladım", {"toxic": False}),
    ("Bugün 25 dakika odaklandım, çok verimli geçti", {"toxic": False}),
    ("Bildirimleri kapattım, rahatça çalıştım", {"toxic": False}),
    ("Plan yapmak işleri kolaylaştırıyor", {"toxic": False}),
    ("Dikkat dağınıklığıyla başa çıkmak için yöntemler", {"toxic": False}),
    ("Mola vermek çalışmanın parçası", {"toxic": False}),
    ("Rutin oluşturmak disiplini artırır", {"toxic": False}),
    ("Sessiz bir ortamda çalışmak çok faydalı", {"toxic": False}),
    ("Verimli olmak için öncelik belirlemek gerekiyor", {"toxic": False}),
    ("Pomodoro tekniği denedim, beğendim", {"toxic": False}),
    ("Görev listesi yapmak işleri düzenler", {"toxic": False}),
    ("Nefes egzersizi stresi azaltıyor", {"toxic": False}),
    ("Dengeyi bulmak önemli, hem iş hem özel hayat", {"toxic": False}),
    ("Kesintisiz çalışma zararlı, mola şart", {"toxic": False}),
    ("Adım adım ilerlemek en sağlıklısı", {"toxic": False}),
    ("TEKNOFEST bu yıl çok büyük bir organizasyon oldu", {"toxic": False, "sentiment_pos": True}),
    ("TEKNOFESTe katılmak öğrenciler için büyük bir fırsat", {"toxic": False, "sentiment_pos": True}),
    ("Uluslararası arenada Türkiye çok güçlü projeler sunuyor", {"toxic": False, "sentiment_pos": True}),
    ("Gençlerin teknolojiye olan ilgisi her yıl artıyor", {"toxic": False, "sentiment_pos": True}),
    ("Yapay zeka destekli projeler geleceğin teknolojisi", {"toxic": False, "sentiment_pos": True}),
    ("AR-GE yatırımları ülkemizin geleceğini şekillendiriyor", {"toxic": False, "sentiment_pos": True}),
    ("Dünyanın dört bir yanından katılımcılar geliyor", {"toxic": False, "sentiment_pos": True}),
    ("Bilim ve teknoloji festivali çok heyecan verici", {"toxic": False, "sentiment_pos": True}),
    ("Yarışma projeleri gerçek sorunlara çözümler üretiyor", {"toxic": False, "sentiment_pos": True}),
    ("Mentörlük desteği projelerin kalitesini artırıyor", {"toxic": False, "sentiment_pos": True}),
    ("Üniversite öğrencileri için harika bir deneyim", {"toxic": False, "sentiment_pos": True}),
    ("Lise öğrencileri de büyük projelere imza atıyor", {"toxic": False, "sentiment_pos": True}),
    ("T3 Vakfı gençlere çok güzel fırsatlar sunuyor", {"toxic": False, "sentiment_pos": True}),
    ("Teknoloji yarışmaları inovasyonu teşvik ediyor", {"toxic": False, "sentiment_pos": True}),
    ("Projeler yatırımcılarla buluşturuluyor, girişimcilik destekleniyor", {"toxic": False, "sentiment_pos": True}),
    ("Sosyal medya teknolojileri alanında yeni projeler geliştiriliyor", {"toxic": False, "sentiment_pos": True}),
    ("Dijital refah konusu artık çok önemli", {"toxic": False, "sentiment_pos": True}),
    ("Kullanıcı deneyimi tasarımında yenilikçi yaklaşımlar", {"toxic": False, "sentiment_pos": True}),
    ("Ekip çalışması ve proje yönetimi becerileri gelişiyor", {"toxic": False, "sentiment_pos": True}),
]

SPAM_DATA = [
    ("BEDAVA KAZAN!!! HEMEN TIKLA İNANILMAZ FIRSAT", {"spam": True}),
    ("DM AT KAZANCI GARANTİLE, SON FIRSAT!!!", {"spam": True}),
    ("Takip et, hediye kazan, kaçırma bu fırsatı", {"spam": True}),
    ("İnanılmaz fırsat, sadece bugün, tıkla ve al", {"spam": True}),
    ("Kredi kartı bilgilerinle hemen kazanmaya başla", {"spam": True}),
    ("Garanti kazanç, haftada 10000 TL, hemen başla", {"spam": True}),
    ("Son dakika fırsat, bedava çekiliş, link bio'da", {"spam": True}),
    ("Hemen tıkla, bedava ürün kazan, fırsatı kaçırma", {"spam": True}),
    ("Sana özel fırsat, hemen tıkla ve al", {"spam": True}),
    ("Kazancını katla, sadece bir tık uzağında", {"spam": True}),
    ("Link bio'da, hemen tıkla, bedava kazan", {"spam": True}),
    ("Bu fırsatı kaçırma, hemen başla", {"spam": True}),
    ("Haftada 5000 TL kazan, garanti kazanç", {"spam": True}),
    ("İnanılmaz fırsat, son 24 saat, tıkla", {"spam": True}),
    ("Seni de bekliyoruz, hemen DM at", {"spam": True}),
    ("Takip et kazan, her gün yeni çekiliş", {"spam": True}),
    ("Bedenava deneme, hemen başla, kaçırma", {"spam": True}),
    ("Kredi kartı gerekmez, hemen tıkla", {"spam": True}),
    ("Günde 5 dakika ile kazanmaya başla", {"spam": True}),
    ("Yatırım tavsiyesi, garanti getiri, hemen başla", {"spam": True}),
]

CLEAN_NOT_SPAM = [
    ("Bu makale çok faydalı, herkesin okumasını öneririm", {"spam": False}),
    ("Yeni bir blog yazısı yazdım, link bio'da", {"spam": False}),
    ("Bugün çok güzel bir gün geçirdim", {"spam": False}),
    ("Bu konuyu merak edenler için bilgi paylaşıyorum", {"spam": False}),
    ("Kitap önerisi: bu kitabı mutlaka okuyun", {"spam": False}),
    ("Yürüyüşe çıktım, hava çok güzeldi", {"spam": False}),
    ("Bu restoranın yemekleri çok lezzetli", {"spam": False}),
    ("Spor salonuna gittim, çok iyi hissediyorum", {"spam": False}),
    ("Yeni bir hobi edindim, çok eğlenceli", {"spam": False}),
    ("Bu filmi izledim, çok beğendim", {"spam": False}),
    ("Akşam yemeği pişirdim, tarifini paylaşıyorum", {"spam": False}),
    ("Tatil planı yapıyoruz, önerilerinizi bekliyorum", {"spam": False}),
    ("Bu şarkıyı herkese tavsiye ederim", {"spam": False}),
    ("Sabah sporu yapıyorum, çok faydalı", {"spam": False}),
    ("Bu konuda tecrübelerimi paylaşmak istiyorum", {"spam": False}),
    ("Hafta sonu kamp yapacağız, heyecanlıyım", {"spam": False}),
    ("Yeni bir kursa başladım, çok güzel geçiyor", {"spam": False}),
    ("Bu restoranın menüsü çok çeşitli", {"spam": False}),
    ("Doğada yürüyüş yapmak çok rahatlatıcı", {"spam": False}),
    ("Bu bilgiyi Useful buldum, kaydettim", {"spam": False}),
]

# ── Mode-specific data ───────────────────────────────────────────────────

FOCUS_DATA = [
    ("Derin çalışma seanslarım 25 dakika sürüyor, çok verimli", {"focus": True}),
    ("Pomodoro tekniği ile odak süremi artırdım", {"focus": True}),
    ("Bildirimleri kapattım, kesintisiz çalışıyorum", {"focus": True}),
    ("Sabah rutinim: plan yap, önceliklendir, başla", {"focus": True}),
    ("Dikkat dağınıklığı için en iyi yöntem: tek görev", {"focus": True}),
    ("Mola vermek çalışmanın parçası, 5 dakika yeterli", {"focus": True}),
    ("Sessiz bir oda, kahve ve plan: mükemmel formül", {"focus": True}),
    ("Görev listesi hazırladım, sırayla ilerliyorum", {"focus": True}),
    ("Kesintisiz çalışmak için telefonumu başka odaya bıraktım", {"focus": True}),
    ("Verimli olmak için öncelik belirlemek şart", {"focus": True}),
    ("Adım adım ilerlemek en sağlıklısı", {"focus": True}),
    ("Nefes egzersizi yapıp başlıyorum, sakinleşiyorum", {"focus": True}),
    ("Checklist kullanmak işleri çok kolaylaştırıyor", {"focus": True}),
    ("Dikkat süremi 30 dakikaya çıkardım, gururluyum", {"focus": True}),
    ("Odak modunda 2 saat çalıştım, harika hissediyorum", {"focus": True}),
    ("Rutin oluşturmak disiplini artırır", {"focus": True}),
    ("Sabahları erken kalkıp plan yapıyorum", {"focus": True}),
    ("Çalışma alanımı düzenledim, çok daha iyi odaklanıyorum", {"focus": True}),
    ("Dikkat dağıtıcıları listesini çıkardım, hepsini engelledim", {"focus": True}),
    ("Zaman bloklama tekniğini deniyorum, çok etkili", {"focus": True}),
]

LEARN_DATA = [
    ("Bugün makine öğrenmesi hakkında yeni bir şey öğrendim", {"learn": True}),
    ("Bu konuyu araştırıyorum, ilginç bilgiler var", {"learn": True}),
    ("Kavramı kendi cümlelerimle açıkladım, şimdi anladım", {"learn": True}),
    ("Birine öğretince kendim de daha iyi anlıyorum", {"learn": True}),
    ("Kaynak okumak, video izlemekten daha etkili", {"learn": True}),
    ("Analiz yapmak verileri anlamak için önemli", {"learn": True}),
    ("Yöntem: oku, anla, açıkla, örnek ver, öğret", {"learn": True}),
    ("Bugün bilim hakkında ilginç bir makale okudum", {"learn": True}),
    ("Model eğitimi için veri hazırlığı çok önemli", {"learn": True}),
    ("Kanıta dayalı düşünmek her zaman en doğrusu", {"learn": True}),
    ("Bu kitapta çok güzel örnekler var", {"learn": True}),
    ("Eğitim hayat boyu süren bir yolculuk", {"learn": True}),
    ("Veri analitiği günümüzün en önemli becerisi", {"learn": True}),
    ("Öğrenme stratejileri hakkında araştırma yaptım", {"learn": True}),
    ("Nasıl daha iyi öğrenebilirim diye düşündüm", {"learn": True}),
    ("Bu konuda ders notlarımı paylaşıyorum", {"learn": True}),
    ("Araştırma sonuçları çok ilginç", {"learn": True}),
    ("Model nedir, nasıl çalışır, detaylı anlattım", {"learn": True}),
    ("Bilimsel yöntemi uygulamak gerekiyor", {"learn": True}),
    ("Tanım ve kavramları netleştirmek önemli", {"learn": True}),
]

FUN_DATA = [
    ("Bugün çok komik bir video izledim, gülmekten yıkıldım", {"fun": True}),
    ("Arkadaşlarımla oyun gecesi yaptık, çok eğlendik", {"fun": True}),
    ("Hafta sonu sinemaya gittik, harika bir filmdi", {"fun": True}),
    ("Sahilde yürüyüş yapıp kahve içtik", {"fun": True}),
    ("Mizah paylaşımları günümü güzelleştiriyor", {"fun": True}),
    ("En sevdiğim albümü dinledim, çok keyifliydi", {"fun": True}),
    ("Kahve eşliğinde sohbet etmek en güzel aktivite", {"fun": True}),
    ("Komik bir meme attım, herkes beğendi", {"fun": True}),
    ("Eğlenceli bir etkinlik oldu, herkes katıldı", {"fun": True}),
    ("Film önerisi: bu filmi mutlaka izleyin, çok güzel", {"fun": True}),
    ("Oyun oynadık, çok eğlendik", {"fun": True}),
    ("Yürüyüş yaparken müzik dinledim, harika hissettim", {"fun": True}),
    ("Güzel bir gün geçirdim, keyifliydi", {"fun": True}),
    ("Albüm çıkarmış, hemen dinledim, beğendim", {"fun": True}),
    ("Arkadaşlarla buluştuk, sohbet ettik, güldük", {"fun": True}),
    ("Bugün neşeli bir gün geçiriyorum", {"fun": True}),
    ("Mizah her şeyin ilacıdır", {"fun": True}),
    ("Keyifli bir akşam geçirdim", {"fun": True}),
    ("Film ve kahve ikilisi mükemmel", {"fun": True}),
    ("Eğlence de paylaşılabilir, bağırmadan", {"fun": True}),
]

# ── Feature Extraction ───────────────────────────────────────────────────

def build_dataset():
    texts, labels = [], []

    # Task 1: Toxicity (binary)
    for text, meta in TOXIC_DATA:
        texts.append(text)
        labels.append({"toxic": 1, "spam": 0, "sentiment": -1, "mode": "neutral"})
    for text, meta in CLEAN_DATA:
        texts.append(text)
        labels.append({"toxic": 0, "spam": 0, "sentiment": 1, "mode": "neutral"})
    for text, meta in SPAM_DATA:
        texts.append(text)
        labels.append({"toxic": 0, "spam": 1, "sentiment": 0, "mode": "neutral"})
    for text, meta in CLEAN_NOT_SPAM:
        texts.append(text)
        labels.append({"toxic": 0, "spam": 0, "sentiment": 1, "mode": "neutral"})

    # Mode-specific data
    for text, meta in FOCUS_DATA:
        texts.append(text)
        labels.append({"toxic": 0, "spam": 0, "sentiment": 1, "mode": "focus"})
    for text, meta in LEARN_DATA:
        texts.append(text)
        labels.append({"toxic": 0, "spam": 0, "sentiment": 1, "mode": "learn"})
    for text, meta in FUN_DATA:
        texts.append(text)
        labels.append({"toxic": 0, "spam": 0, "sentiment": 1, "mode": "fun"})

    return texts, labels


def train_and_export():
    texts, labels = build_dataset()

    y_toxic = np.array([l["toxic"] for l in labels])
    y_spam = np.array([l["spam"] for l in labels])
    y_sentiment = np.array([l["sentiment"] for l in labels])
    y_mode = np.array([l["mode"] for l in labels])

    X_train, X_test, yt_tr, yt_te = train_test_split(texts, y_toxic, test_size=0.2, random_state=42)
    _, _, ys_tr, ys_te = train_test_split(texts, y_spam, test_size=0.2, random_state=42)
    _, _, yse_tr, yse_te = train_test_split(texts, y_sentiment, test_size=0.2, random_state=42)
    _, _, ym_tr, ym_te = train_test_split(texts, y_mode, test_size=0.2, random_state=42)

    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 5),
        max_features=8000,
        sublinear_tf=True,
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
    print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")

    # Train individual models
    toxic_model = LogisticRegression(C=5.0, max_iter=500, class_weight="balanced")
    toxic_model.fit(X_train_tfidf, yt_tr)
    toxic_acc = toxic_model.score(X_test_tfidf, yt_te)
    print(f"Toxicity accuracy: {toxic_acc:.3f}")

    spam_model = LogisticRegression(C=5.0, max_iter=500, class_weight="balanced")
    spam_model.fit(X_train_tfidf, ys_tr)
    spam_acc = spam_model.score(X_test_tfidf, ys_te)
    print(f"Spam accuracy: {spam_acc:.3f}")

    sentiment_model = LogisticRegression(C=5.0, max_iter=500, class_weight="balanced")
    sentiment_model.fit(X_train_tfidf, yse_tr)
    sentiment_acc = sentiment_model.score(X_test_tfidf, yse_te)
    print(f"Sentiment accuracy: {sentiment_acc:.3f}")

    mode_model = LogisticRegression(C=5.0, max_iter=500, class_weight="balanced")
    mode_model.fit(X_train_tfidf, ym_tr)
    mode_acc = mode_model.score(X_test_tfidf, ym_te)
    print(f"Mode fit accuracy: {mode_acc:.3f}")

    # ── Export to ONNX ──
    out_dir = Path("backend/app/ml_models")
    out_dir.mkdir(parents=True, exist_ok=True)

    n_features = len(vectorizer.vocabulary_)
    initial_type = [("input", FloatTensorType([None, n_features]))]

    for name, model in [
        ("toxicity", toxic_model),
        ("spam", spam_model),
        ("sentiment", sentiment_model),
        ("mode_fit", mode_model),
    ]:
        onnx_model = convert_sklearn(model, initial_types=initial_type)
        onnx_path = out_dir / f"{name}.onnx"
        with open(onnx_path, "wb") as f:
            f.write(onnx_model.SerializeToString())
        print(f"Exported: {onnx_path}")

    # Save vectorizer vocabulary and config
    config = {
        "n_features": n_features,
        "analyzer": "char_wb",
        "ngram_range": [2, 5],
        "max_features": 8000,
        "sublinear_tf": True,
        "model_version": "tfidf-lr-v1",
        "metrics": {
            "toxicity_acc": round(float(toxic_acc), 3),
            "spam_acc": round(float(spam_acc), 3),
            "sentiment_acc": round(float(sentiment_acc), 3),
            "mode_acc": round(float(mode_acc), 3),
        },
    }

    config_path = out_dir / "model_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"Config saved: {config_path}")

    # Save vectorizer separately (for inference)
    import pickle
    vec_path = out_dir / "vectorizer.pkl"
    with open(vec_path, "wb") as f:
        pickle.dump(vectorizer, f)
    print(f"Vectorizer saved: {vec_path}")

    print("\n✅ Training complete!")
    print(f"   Models: {out_dir}")
    return config


if __name__ == "__main__":
    train_and_export()
