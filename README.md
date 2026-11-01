# Claude Model Starter

Claude Model Starter is a small FastAPI service that gives you one HTTP endpoint for text generation. It supports two providers:

1. **Anthropic API** - sends prompts to hosted Claude Sonnet or Claude Opus models.
2. **Local Hugging Face model** - runs an open-source text-generation model on your own machine.

The service selects the provider with an environment variable, so application code does not need to change when you switch providers.

> This project does not contain, download, or recreate Claude's proprietary model weights. Claude is accessed through Anthropic's API. The local option uses a separate open-source model.

## What it does

- Starts an HTTP API at `http://localhost:8000`.
- Accepts a text prompt through `POST /chat`.
- Uses Claude Sonnet by default when `MODEL_PROVIDER=anthropic`.
- Lets each request select a different Anthropic model with the `model` field.
- Supports a local Hugging Face model when `MODEL_PROVIDER=local`.
- Loads the local model once and reuses it for later requests.
- Limits prompt size and generated token count through request validation.
- Provides `GET /health` for a basic service health check.
- Keeps API keys in `.env`, which is excluded from Git.

## Requirements

- Python 3.10 or newer
- An Anthropic API key for the Anthropic provider
- A capable CPU/GPU and sufficient memory for local inference
- Internet access the first time a Hugging Face model is downloaded

## Installation

```bash
git clone <your-repository-url>
cd claude-model-starter

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Anthropic Claude usage

1. Create an API key in the [Anthropic Console](https://console.anthropic.com/).
2. Open `.env`.
3. Set `ANTHROPIC_API_KEY` to your key.
4. Keep `MODEL_PROVIDER=anthropic`.
5. Start the server:

```bash
uvicorn app:app --reload
```

Call the API:

```bash
curl -X POST http://localhost:8000/chat \
  -H "content-type: application/json" \
  -d '{"message":"Explain recursion in simple terms"}'
```

Example response:

```json
{
  "provider": "anthropic",
  "model": "claude-sonnet-4-5",
  "response": "..."
}
```

To select a model for one request:

```bash
curl -X POST http://localhost:8000/chat \
  -H "content-type: application/json" \
  -d '{"message":"Review this design","model":"claude-opus-4-1","max_tokens":2048}'
```

Use model IDs that are currently available to your Anthropic account. You can also set the default in `.env` with `ANTHROPIC_MODEL`.

## Local model usage

The default requirements install the API and Anthropic client. To enable the local provider, install PyTorch and Transformers:

```bash
pip install torch transformers
```

Then update `.env`:

```dotenv
MODEL_PROVIDER=local
LOCAL_MODEL_ID=Qwen/Qwen2.5-1.5B-Instruct
MAX_TOKENS=256
```

Start the server normally:

```bash
uvicorn app:app --reload
```

The model is downloaded from Hugging Face on its first use and cached locally. Replace `LOCAL_MODEL_ID` with another compatible text-generation model if desired. Larger models require substantially more RAM or GPU memory.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `MODEL_PROVIDER` | `anthropic` | Provider: `anthropic` or `local` |
| `ANTHROPIC_API_KEY` | empty | API key used for Anthropic requests |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-5` | Default Anthropic model |
| `LOCAL_MODEL_ID` | `Qwen/Qwen2.5-1.5B-Instruct` | Hugging Face model used locally |
| `MAX_TOKENS` | `1024` | Default maximum generated tokens |

Request-level `max_tokens` overrides `MAX_TOKENS` and must be between 1 and 8192. Request-level `model` overrides `ANTHROPIC_MODEL` for Anthropic requests.

## API reference

### `GET /health`

Checks that the API process is running:

```bash
curl http://localhost:8000/health
```

Response:

```json
{"status":"ok","provider":"anthropic"}
```

### `POST /chat`

Request body:

```json
{
  "message": "Your prompt",
  "model": "optional-model-id",
  "max_tokens": 1024
}
```

`message` is required and may contain 1 to 100,000 characters. `model` and `max_tokens` are optional.

Response body:

```json
{
  "provider": "anthropic",
  "model": "claude-sonnet-4-5",
  "response": "Generated text"
}
```

## Interactive API documentation

With the server running, FastAPI provides:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Docker

Build and run the API:

```bash
docker build -t claude-model-starter .
docker run --rm -p 8000:8000 --env-file .env claude-model-starter
```

The included Docker image installs the API and Anthropic dependencies. For local inference, create an image with PyTorch and Transformers added to the dependencies, and provide enough memory for the selected model.

## Project files

| File | Purpose |
|---|---|
| `app.py` | FastAPI application and provider implementations |
| `.env.example` | Configuration template |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Container image definition |
| `.gitignore` | Excludes secrets, environments, caches, and model files |

## Troubleshooting

### `ANTHROPIC_API_KEY is not configured`

Set the key in `.env`, confirm that the file is in the project directory, and restart the server.

### `Local inference requires transformers and torch`

Install the optional local dependencies:

```bash
pip install torch transformers
```

### Model access or model ID errors

Check that the model ID is valid, available on Hugging Face, and compatible with the `text-generation` pipeline.

### Requests are slow locally

Local generation depends on hardware. Use a smaller model, reduce `MAX_TOKENS`, or configure an appropriate PyTorch GPU installation.

## Security and cost

- Never commit `.env` or expose `ANTHROPIC_API_KEY`.
- Add authentication and rate limiting before exposing this API publicly.
- Anthropic requests may incur usage charges according to your Anthropic account.
- Local inference does not send prompts to Anthropic, but downloaded model files and generated output still consume local resources.

## License

Add the license appropriate for your project before publishing. The service is an integration example and does not grant rights to Claude or third-party model weights.
