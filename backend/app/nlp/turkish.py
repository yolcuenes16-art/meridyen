import re
import unicodedata

_SUFFIXES = (
    "laştır",
    "leştir",
    "lar",
    "ler",
    "mız",
    "miz",
    "muz",
    "müz",
    "nız",
    "niz",
    "nuz",
    "nüz",
    "dan",
    "den",
    "tan",
    "ten",
    "daki",
    "deki",
    "nın",
    "nin",
    "nun",
    "nün",
    "yı",
    "yi",
    "yu",
    "yü",
    "sı",
    "si",
    "su",
    "sü",
    "lık",
    "lik",
    "luk",
    "lük",
    "cı",
    "ci",
    "cu",
    "cü",
    "ça",
    "çe",
    "ken",
    "yor",
    "mek",
    "mak",
    "mış",
    "miş",
    "muş",
    "müş",
    "dı",
    "di",
    "du",
    "dü",
    "tı",
    "ti",
    "tu",
    "tü",
    "arak",
    "erek",
)


def normalize_tr(text: str) -> str:
    lowered = text.replace("I", "ı").replace("İ", "i").lower()
    lowered = unicodedata.normalize("NFC", lowered)
    lowered = re.sub(r"(.)\1{2,}", r"\1\1", lowered)
    return lowered


def stem_token(token: str) -> str:
    stem = token
    for _ in range(3):
        trimmed = False
        for suffix in _SUFFIXES:
            if stem.endswith(suffix) and len(stem) - len(suffix) >= 3:
                stem = stem[: -len(suffix)]
                trimmed = True
                break
        if not trimmed:
            break
    return stem


def tokenize(text: str) -> list[str]:
    return [token for token in re.split(r"[^\wçğıöşü]+", text) if token]
