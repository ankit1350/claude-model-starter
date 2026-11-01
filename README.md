# Claude Model Starter

A small API that supports:

- Anthropic Claude Sonnet or Opus through the Anthropic API.
- A local Hugging Face text-generation model through `transformers`.

This project does **not** contain or recreate Claude's proprietary model weights. It calls Anthropic's hosted models when `MODEL_PROVIDER=anthropic`.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --reload
```

Set `ANTHROPIC_API_KEY` in `.env`, then call:

```bash
curl -X POST http://localhost:8000/chat \
  -H 'content-type: application/json' \
  -d '{"message":"Explain recursion simply","model":"claude-sonnet-4-5"}'
```

For local inference, set `MODEL_PROVIDER=local` and optionally `LOCAL_MODEL_ID` to a compatible Hugging Face model. Local inference requires a capable machine and may need PyTorch-specific installation instructions.

## Configuration

See `.env.example`. The default provider is `anthropic`, and the default model is Sonnet. Use a current model ID available to your Anthropic account.

## Safety

Never commit `.env` or API keys. The included `.gitignore` excludes local secrets and model caches.
