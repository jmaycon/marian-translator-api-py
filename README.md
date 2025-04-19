# Marian Translator German ↔ English

Simple REST API for German ↔ English translation using Hugging Face MarianMT models.

---

## Run

### Option 2: On Linux

UI: http://localhost:30002/

```shell
chmod +x run_local.sh
./run_local.sh
```

### Option 2: On Windows (PowerShell)

UI: http://localhost:30003/

```shell
./run_local.ps1
```

### Option 3: Run with Docker 🐳

UI: http://localhost:30004/

```shell
docker build -t argos-translator-api-py .
docker run --rm -p 30004:8080 argos-translator-api-py 
```
---

## 🔁 API Usage

To check if CUDA is available run

```shell
source venv/bin/activate
python -c "import torch; print(torch.cuda.is_available())"
```
_For powershell use `.\win-venv\Scripts\Activate.ps1`_

### POST `/translate-<cpu|gpu>`



Translate text between German and English.

`direction` options:

- `"de-en"` = German → English
- `"en-de"` = English → German

#### Sample Request (with curl)

1.German to English

```shell
curl -X POST http://localhost:8081/translate-cpu \
      -H "Content-Type: application/json" \
      -d '{"text": "Guten Morgen", "direction": "de-en"}'
```

- 2.English to German

```shell
curl -X POST http://localhost:8080/translate-cpu \
      -H "Content-Type: application/json" \
      -d '{"text": "Hi my friend", "direction": "en-de"}'
```

#### Sample Response

```json
{
  "translation": "Good morning"
}
```
---

## 🧩 Models Used

- https://huggingface.co/Helsinki-NLP/opus-mt-de-en
- https://huggingface.co/Helsinki-NLP/opus-mt-en-de


