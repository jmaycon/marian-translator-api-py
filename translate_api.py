from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from transformers import MarianMTModel, MarianTokenizer
import torch
import traceback
import logging
from concurrent.futures import ThreadPoolExecutor
import syntok.segmenter as segmenter  # Use syntok's correct segmenter module

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = FastAPI()

# Serve static files (e.g., HTML, JS, CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

# Define devices
CPU = torch.device("cpu")
CUDA = torch.device("cuda") if torch.cuda.is_available() else None

# Load models for both directions once, to specific devices
models = {
    "cpu": {
        "de-en": {
            "tokenizer": MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-de-en"),
            "model": MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-de-en").to(CPU),
        },
        "en-de": {
            "tokenizer": MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-de"),
            "model": MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-de").to(CPU),
        },
    }
}

# Load GPU models if available
if CUDA:
    models["gpu"] = {
        "de-en": {
            "tokenizer": models["cpu"]["de-en"]["tokenizer"],  # reuse tokenizer
            "model": MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-de-en").to(CUDA),
        },
        "en-de": {
            "tokenizer": models["cpu"]["en-de"]["tokenizer"],
            "model": MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-de").to(CUDA),
        },
    }

# Input data model
class TranslationRequest(BaseModel):
    text: str
    direction: str  # "de-en" or "en-de"

# Sentence splitting using syntok.segmenter (modern and lightweight alternative to nltk)
def split_into_sentences(text: str):
    sentences = []
    for paragraph in segmenter.process(text):
        for sentence in paragraph:
            sentences.append(" ".join(token.value for token in sentence))
    return sentences

# Translate a list of sentences using the provided tokenizer/model
def translate_sentences(sentences, tokenizer, model, device):
    translations = []
    for sentence in sentences:
        inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True).to(device)
        outputs = model.generate(**inputs)
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        translations.append(decoded)
    return translations

# Translate text in parallel by sentence for large input support
def parallel_translate(text, tokenizer, model, device):
    sentences = split_into_sentences(text)
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(translate_sentences, [s], tokenizer, model, device) for s in sentences]
        results = [future.result()[0] for future in futures]
    return " ".join(results)

# Unified translation logic for both CPU and GPU
def perform_translation(device_key: str, request: TranslationRequest):
    device = CPU if device_key == "cpu" else CUDA

    if device is None:
        raise HTTPException(status_code=503, detail=f"{device_key.upper()} not available on this system.")

    if request.direction not in models[device_key]:
        raise HTTPException(status_code=400, detail="Invalid direction (use 'de-en' or 'en-de')")

    try:
        config = models[device_key][request.direction]
        return {
            "translation": parallel_translate(
                request.text, config["tokenizer"], config["model"], device
            )
        }
    except Exception as e:
        logger.error(f"{device_key.upper()} translation failed:\n" + traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

# Translation endpoint for CPU
@app.post("/translate-cpu")
def translate_cpu(request: TranslationRequest):
    return perform_translation("cpu", request)

# Translation endpoint for GPU
@app.post("/translate-gpu")
def translate_gpu(request: TranslationRequest):
    return perform_translation("gpu", request)