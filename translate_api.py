from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from transformers import MarianMTModel, MarianTokenizer

app = FastAPI()

# Serve static files like CSS/JS if needed
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route to return index.html
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

# Translation logic
de_en_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-de-en")
de_en_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-de-en")

en_de_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-de")
en_de_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-de")

class TranslationRequest(BaseModel):
    text: str
    direction: str  # "de-en" or "en-de"

@app.post("/translate")
def translate(request: TranslationRequest):
    if request.direction == "de-en":
        tokenizer, model = de_en_tokenizer, de_en_model
    elif request.direction == "en-de":
        tokenizer, model = en_de_tokenizer, en_de_model
    else:
        return {"error": "Invalid direction"}

    tokens = tokenizer(request.text, return_tensors="pt", padding=True)
    translated = model.generate(**tokens)
    output = tokenizer.decode(translated[0], skip_special_tokens=True)

    return {"translation": output}
