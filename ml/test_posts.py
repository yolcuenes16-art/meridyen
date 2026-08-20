from backend.app.services.analysis_service import ContentAnalysisService
svc = ContentAnalysisService()
tests = [
    "TEKNOFESTin teknoloji yarismalari artik uluslararasi arenada da taniniyor. Dunyanin dort bir yanindan gencler Turkiyeye gelip projelerini sunuyor.",
    "TEKNOFEST bu yil Sanliurfada duzenleniyor. 30 Eylul - 4 Ekim tarihlerinde birbirinden yenilikci projeler juri karsisina cikacak.",
    "TEKNOFESTe katilmak universiteli ogrenciler icin muhtesem bir deneyim.",
    "NSosyal Inovasyon Yarismasinin en guzel yani toplumsal faydayi da degerlendirme kriterlerine almasi.",
    "TEKNOFEST sadece bir yarisma degil Turkiye teknoloji ekosisteminin yatirimi.",
    "BEDAVA KAZAN HEMEN TIKLA FIRSAT GARANTi",
]
for p in tests:
    a = svc.analyze(p, p, "Teknoloji")
    pub = "OK" if a.safety_score >= 60 and a.spam_score < 60 and "toksik" not in a.flags else "BLOCKED"
    print(f"Q:{a.quality_score:5.1f} S:{a.safety_score:5.1f} W:{a.wellbeing_score:5.1f} {pub:7s} | {p[:60]}")
