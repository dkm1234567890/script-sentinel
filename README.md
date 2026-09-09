# Script Sentinel

Script Sentinel is a source-backed screenplay pre-clearance research assistant built for the Parallel track of Agentic Cinema: The Blockbuster Hackathon.

A user uploads a screenplay PDF. Gemini extracts real-world references, a Google ADK agent actively calls Parallel Search for current evidence, and the app returns a prioritized, cited human-review queue.

> Script Sentinel provides research triage, not legal advice or a clearance decision. A qualified reviewer must verify sources and make final legal and production decisions.

## Runtime architecture

```text
Web browser -> FastAPI on Cloud Run
                  |-> Gemini on Google Cloud: PDF extraction
                  |-> Google ADK agent
                         |-> parallel-web Search API tool
                         |-> Gemini evidence assessment
                  |-> cited JSON + report UI
```

The Parallel integration is implemented in `app/parallel_tool.py`. The official `parallel-web` SDK is imported and `Parallel.search(...)` is called at runtime. The function is registered as a tool on the ADK agent in `app/pipeline.py`.

## Features

- Native Gemini PDF understanding with structured output
- Reference categories for people, brands, quotations, facts, and locations
- Real Parallel Search calls with source URLs and excerpts
- ADK-based tool orchestration
- Human-review statuses and explicit uncertainty
- Responsive report interface and JSON export
- Upload validation, bounded reference count, and graceful per-item failures

## Requirements

- Python 3.11 or newer
- A Google Cloud project with Vertex AI / Gemini access
- Google Cloud Application Default Credentials
- A Parallel API key

## Local setup

For nontechnical instructions, read [BEGINNER_SETUP_GUIDE.md](BEGINNER_SETUP_GUIDE.md).

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, fill the values privately, export them into the terminal, and run:

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. Health status is available at `/health`.

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

The included tests do not call paid external APIs. A real end-to-end test requires configured Google Cloud and Parallel credentials.

## Deploy to Cloud Run

Set the project variables and store the Parallel key in Secret Manager. Never put the key directly in the command history or repository.

```bash
gcloud run deploy script-sentinel \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,GOOGLE_CLOUD_LOCATION=global,GOOGLE_GENAI_USE_ENTERPRISE=true,GEMINI_MODEL=gemini-2.5-flash \
  --set-secrets PARALLEL_API_KEY=parallel-api-key:latest
```

The Cloud Run service account needs permission to call the required Google Cloud AI service and access the named secret.

## Privacy and safety

- Uploaded bytes remain in memory for the request and are not intentionally persisted by the app.
- Screenplay text and secrets are not logged by application code.
- Missing search results are reported as insufficient evidence, never as proof of safety.
- The sample screenplay is original and contains no commercial screenplay or copyrighted lyrics.
- Production deployments should add authentication, retention controls, and a formal privacy review.

## Limitations

- The MVP is optimized for text-based PDFs.
- Search evidence may be incomplete or conflicting.
- The model can still make extraction or classification errors.
- The tool does not determine ownership, licensing terms, or legal clearance.
- Qualified human review remains required.

## Findings and learnings

The build reinforced that clearance research needs both semantic document understanding and current, traceable evidence. A staged workflow is easier to audit than one large prompt. Explicit uncertainty is a product feature: it prevents missing evidence from being misrepresented as a clear result.

## License

MIT. See [LICENSE](LICENSE).
