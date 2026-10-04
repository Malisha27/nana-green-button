# 🟢 Nana, Press the Green Button

A tiny WhatsApp helper for my grandparents. Big buttons, simple steps, English / Hindi / Marathi.
Powered by Google's open-weight **Gemma 4** model via the free Gemini API.

Built for the DEV Hacktoberfest Weekend Challenge: Build for a Friend (Oct 2026).

## Run it

1. Get a free API key at https://aistudio.google.com/apikey
2. Install and run:

```powershell
pip install -r requirements.txt
$env:GEMINI_API_KEY="your-key-here"      # Mac/Linux: export GEMINI_API_KEY="your-key-here"
streamlit run app.py --server.address 0.0.0.0
```

On the laptop: open http://localhost:8501

On a phone (same WiFi): open `http://<laptop-ip>:8501`. Find the IP with `ipconfig` (Windows, "IPv4 Address"). Add it to the home screen so it opens like an app.

## How it works
- `WHATSAPP_NOTES` in `app.py` is a hand-written cheat sheet of WhatsApp steps.
- Gemma is told to answer only from those notes, in max 5 steps, in the chosen language, describing buttons by colour and shape.
- Low temperature keeps answers consistent.

## Run fully offline (optional)
Gemma is open-weight, so the same idea runs locally with Ollama (`ollama pull gemma3:1b`). I tried this first; on my laptop it was too slow for a good demo, so I used the hosted Gemma instead.
