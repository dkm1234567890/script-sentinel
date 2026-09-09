# Devpost submission copy

## Project name

Script Sentinel

## Tagline

Source-backed screenplay pre-clearance research with Gemini, Google ADK, and Parallel Search.

## Inspiration

Screenplays can contain dozens of references to real people, organizations, quotations, places, and historical claims. Finding all of them early is repetitive and error-prone. Script Sentinel gives writers and production teams a fast, traceable first-pass research queue before qualified reviewers make final clearance decisions.

## What it does

A user uploads a screenplay PDF. Gemini identifies significant real-world references and preserves their scene context. A Google ADK agent decides how each reference should be researched and actively calls Parallel Search for current web evidence. The application then returns a prioritized report with confidence, rationale, recommended next actions, and clickable sources.

Script Sentinel explicitly distinguishes clear signals, items requiring review, high-attention items, and insufficient evidence. It never presents itself as a replacement for legal counsel.

## How we built it

- Google Agent Development Kit for the agent workflow and tool orchestration
- Gemini on Google Cloud for PDF understanding, structured extraction, and evidence assessment
- Parallel Search API, called at runtime through the official Python SDK, for fresh source-linked evidence
- FastAPI and accessible HTML/CSS/JavaScript for the web product
- Cloud Run for containerized deployment
- Secret Manager for the Parallel API key

## Data sources

The application searches the open web through Parallel Search. Every returned result preserves its source URL, title, relevant excerpt, and available publication date. The demo uses an original synthetic screenplay created for this hackathon.

## Challenges

The hardest product decision was separating research evidence from legal judgment. A missing search result cannot prove that a name is fictional or safe, so the product uses an explicit insufficient-evidence state. We also limited and deduplicated references so a full screenplay does not create an uncontrolled number of searches.

## Accomplishments

- End-to-end PDF-to-report workflow
- Runtime Parallel Search calls visible in the product flow
- Structured, scene-linked findings with traceable citations
- Responsible uncertainty and human-review states
- Deployable Google Cloud architecture

## What we learned

Agentic behavior is most valuable here when it is constrained and auditable. Gemini is effective at understanding screenplay context, while Parallel supplies the current evidence that model memory cannot guarantee. Separating extraction, research, assessment, and reporting makes failures easier to understand and prevents unsupported conclusions.

## What's next

Future versions could compare script revisions, integrate licensed rights databases, assign findings to reviewers, and maintain an evidence history as facts and ownership information change.

## Disclaimer

Script Sentinel provides research triage, not legal advice or a clearance decision. A qualified reviewer must verify sources and make final legal and production decisions.

## Current demo disclosure

Google Cloud billing and authentication could not be completed before submission because the payment portal failed. The repository contains the intended Gemini Enterprise/Vertex AI and Google ADK implementation, but the recorded emergency local demo uses the explicitly labelled Parallel-only fallback for the bundled synthetic screenplay. Its searches and citations are live; Gemini extraction, ADK assessment, and Cloud Run hosting were not executed in that fallback run.
