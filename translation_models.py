from transformers import MarianMTModel, MarianTokenizer
from transformers.utils.hub import cached_file
from transformers.utils import EntryNotFoundError

def is_model_downloaded(model_name: str) -> bool:
    try:
        # Check for presence of model config file in cache
        cached_file(model_name, "config.json")
        return True
    except EntryNotFoundError:
        return False

def install():
    models = [
        "Helsinki-NLP/opus-mt-de-en",
        "Helsinki-NLP/opus-mt-en-de"
    ]

    for model in models:
        if is_model_downloaded(model):
            print(f"✔ Model already downloaded: {model}")
        else:
            print(f"⬇ Downloading model: {model}")
            MarianMTModel.from_pretrained(model)
            MarianTokenizer.from_pretrained(model)


