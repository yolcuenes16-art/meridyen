import httpx

from backend.app.core.config import settings


async def chat_with_llm(messages: list[dict], context: str = "") -> str:
    """Send messages to LLM and get response. Falls back to local analysis if no API key."""
    if not settings.openai_api_key:
        return _fallback_response(messages[-1]["content"] if messages else "")

    system_msg = {
        "role": "system",
        "content": (
            "Sen Meridyen Yapay Zeka Asistani'sin. NSosyal Inovasyon Yarismasi icin gelistirilmis "
            "bir sosyal medya platformunun yapay zeka asistanisin.\n\n"
            "Gorevlerin:\n"
            "- Kullanicinin iceriklerini analiz etmek ve oneriler sunmak\n"
            "- Dijital denge konusunda tavsiyeler vermek\n"
            "- Platform hakkinda yardimci olmak\n"
            "- Icerik kalitesini artirmak icin onerilerde bulunmak\n\n"
            + (f"Platform baglami: {context}\n\n" if context else "")
            + "Her zaman Turkce yanit ver. Kisa ve net ol."
        ),
    }

    all_messages = [system_msg] + messages[-10:]

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.openai_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={
                "model": settings.llm_model,
                "messages": all_messages,
                "max_tokens": 500,
                "temperature": 0.7,
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def summarize_with_llm(content: str) -> str:
    """Summarize content using LLM. Falls back to extractive summary if no API key."""
    if not settings.openai_api_key:
        return _extractive_summary(content)

    messages = [
        {
            "role": "system",
            "content": (
                "Sen bir icerik ozetleme asistanisin. Verilen metni Turkce olarak "
                "kisa ve anlasilir bir sekilde ozetle. Maksimum 3 cumle kullan."
            ),
        },
        {"role": "user", "content": content},
    ]

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.openai_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={
                "model": settings.llm_model,
                "messages": messages,
                "max_tokens": 200,
                "temperature": 0.5,
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


def _fallback_response(prompt: str) -> str:
    """Local fallback when no LLM API key is available."""
    prompt_lower = prompt.lower()

    if any(w in prompt_lower for w in ["merhaba", "selam", "hey", "nasilsin"]):
        return (
            "Merhaba! Ben Meridyen Yapay Zeka Asistaniyim. "
            "Size icerik analizi, dijital denge tavsiyeleri ve platform kullanimi "
            "konusunda yardimci olabilirim. Sormak istediginiz bir sey var mi?"
        )

    if any(w in prompt_lower for w in ["ozet", "ozetle", "kisalt", "kisaca"]):
        return (
            "Icerik ozetleme ozelligini kullanmak icin OpenAI API anahtari gerekli. "
            "Simdilik icin temel cikarimsal ozetleme calisiyor. "
            "Gercek AI destekli ozetleme icin OPENAI_API_KEY ortam degiskenini ayarlayin."
        )

    if any(w in prompt_lower for w in ["tavsiye", "oneri", "dijital denge", "ekranSure"]):
        return (
            "Dijital denge icin oneriler:\n"
            "1. Gunde 2 saat sosyal medya suresini asmamaya calisin.\n"
            "2. Mola verirken ekrandan uzaklasin.\n"
            "3. Olumlu ve yapici icerikleri tercih edin.\n"
            "4. Geceleri ekran mavi isigini azaltin.\n"
            "Detayli analiz icin OPENAI_API_KEY ayarlayarak AI asistanini aktif hale getirebilirsiniz."
        )

    if any(w in prompt_lower for w in ["analiz", "icerik", "kalite", "puan"]):
        return (
            "Iceri analizi icin /api/v1/analysis/content veya /api/v1/analysis/preview "
            "endpointlerini kullanabilirsiniz. AI destekli detayli analiz icin "
            "OPENAI_API_KEY ortam degiskenini ayarlayin."
        )

    if any(w in prompt_lower for w in ["platform", "meridyen", "nasil calisiyor", "ne yapar"]):
        return (
            "Meridyen, NSosyal Inovasyon Yarismasi icin gelistirilmis bir sosyal medya platformudur. "
            "Rizaya dayali kullanim modu, Turkce guvenlik/refah skorlamasi, "
            "seffaf akis yeniden siralama ve gorunurluk carpanli gelir paylasimi sunar. "
            "Gizli duygu cikarimi yoktur."
        )

    return (
        "Meridyen Yapay Zeka Asistani'na hosgeldiniz! "
        "Size icerik analizi, dijital denge tavsiyeleri ve platform hakkinda yardimci olabilirim. "
        "Simdilik sinirli bir yerel modda calisiyorum. "
        "Gercek AI yetenekleri icin OPENAI_API_KEY ortam degiskenini ayarlayin."
    )


def _extractive_summary(text: str, max_chars: int = 150) -> str:
    """Fallback extractive summarization."""
    import re

    text = text.strip()
    if len(text) <= max_chars:
        return text

    sentences = re.split(r"(?<=[.!?])\s+", text)
    meaningful = [s for s in sentences if len(s.strip()) > 10]

    if not meaningful:
        return text[:max_chars].rsplit(" ", 1)[0] + "."

    if len(meaningful) == 1:
        return meaningful[0][:max_chars]

    result = f"{meaningful[0]} {meaningful[1]}"
    if len(result) > max_chars:
        result = meaningful[0][:max_chars].rsplit(" ", 1)[0] + "."

    return result
