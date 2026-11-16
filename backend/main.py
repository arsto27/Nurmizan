import os, json, hmac
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

app = FastAPI(title="Nur Mizan AI API")
ORIGIN = "https://arsto27.github.io"
app.add_middleware(CORSMiddleware, allow_origins=[ORIGIN], allow_methods=["POST","GET"], allow_headers=["Content-Type","X-App-Access"])
class Question(BaseModel):
    question: str = Field(min_length=5,max_length=2000)

@app.get("/health")
def health():
    return {"status":"ok","ai_configured":bool(os.getenv("OPENAI_API_KEY"))}

@app.post("/ask")
def ask(payload: Question, x_app_access: str = Header(default="")):
    access=os.getenv("APP_ACCESS_TOKEN","")
    if not access or not hmac.compare_digest(x_app_access,access):
        raise HTTPException(401,"Erişim kodu geçersiz.")
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(503,"OpenAI API anahtarı sunucuda yapılandırılmamış.")
    path=Path(__file__).with_name("sources.json")
    sources=json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    # Only reviewed, explicitly verified passages may be cited.
    verified=[s for s in sources if s.get("verified") is True and s.get("quote") and s.get("work") and s.get("section")]
    terms=set(payload.question.casefold().split())
    ranked=sorted(verified,key=lambda s:len(terms & set((s.get("quote","")+" "+s.get("topic","")).casefold().split())),reverse=True)
    relevant=[s for s in ranked if len(terms & set((s.get("quote","")+" "+s.get("topic","")).casefold().split()))>0][:5]
    context=json.dumps(relevant,ensure_ascii=False)
    instructions=("Türkçe, dengeli, eleştiriyi adil temsil eden bir araştırma asistanısın. "
        "Yalnızca sağlanan doğrulanmış pasajları Risale-i Nur'dan doğrudan alıntı olarak göster. "
        "Başka hiçbir alıntı, sayfa numarası, eser bölümü veya tarih uydurma. "
        "Kaynak yoksa açıkça 'Bu soru için doğrulanmış Külliyat pasajı henüz eklenmedi' de. "
        "Genel kavramsal değerlendirmeyi açıkça kendi yorumun olarak ayır; doğrulanmamış bilgileri kesinmiş gibi sunma. "
        "Eleştiriye cevap verirken karşı görüşü çarpıtma.")
    try:
        response=OpenAI(timeout=35).responses.create(
            model=os.getenv("OPENAI_MODEL","gpt-5.5"),
            instructions=instructions,
            input="Soru: "+payload.question+"\nDoğrulanmış kaynak pasajları (JSON): "+context,
            max_output_tokens=900)
        return {"answer":response.output_text,"sources":relevant,"source_count":len(relevant)}
    except Exception:
        raise HTTPException(502,"Yapay zekâ servisine erişilemedi. Sunucu kayıtlarını kontrol edin.")
