# Script Sentinel: Beginner Setup and Submission Guide

Follow the steps in order. Do not paste passwords, API keys, payment details, or verification codes into chat or commit them to GitHub.

## Part 1 - Create or confirm the required accounts

### 1. Join the hackathon

1. Open https://agentic-cinema.devpost.com/.
2. Sign in or create a Devpost account.
3. Select **Join hackathon**.
4. Confirm that your country and age meet the eligibility rules.
5. If you have teammates, add them to the Devpost project. The maximum team size is four.

### 2. Prepare Google Cloud

1. Open https://console.cloud.google.com/.
2. Sign in with your Google account.
3. At the top of the page, open the project selector.
4. Choose **New project**.
5. Name it `script-sentinel-hackathon` and create it.
6. Make sure billing is enabled. Google may request a payment method; do not share those details.
7. Open **APIs & Services > Library**.
8. Search for and enable:
   - Vertex AI API
   - Cloud Run Admin API
   - Cloud Build API
   - Artifact Registry API
   - Secret Manager API
9. Note the **Project ID** shown in the project dashboard. The Project ID is not the display name.

### 3. Create the Parallel API key

1. Open https://platform.parallel.ai/.
2. Sign up or sign in.
3. Open the API key area.
4. Create a key and copy it to a password manager or another private location.
5. Never paste this key into chat or put it in a GitHub file.

## Part 2 - Tell Codex only the non-secret status

Reply with:

```text
Google Cloud project ID: [your project ID]
Google Cloud billing enabled: yes/no
Parallel key created: yes/no
Devpost joined: yes/no
GitHub account ready: yes/no
```

The Google Cloud Project ID is safe to share. Do not share the Parallel key.

## Part 3 - Run the application locally

These steps can be completed with help from Codex after Google Cloud is ready.

1. Install the Google Cloud CLI from https://cloud.google.com/sdk/docs/install if it is not installed.
2. Open a terminal in the `script-sentinel` folder.
3. Sign in to Google Cloud:

```powershell
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

4. Create a private local settings file by copying `.env.example` to `.env`.
5. Replace `your-google-cloud-project-id` with the Project ID.
6. Replace `replace-with-your-key` with the Parallel API key. This file is ignored by Git.
7. Create and activate a Python environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

8. Load the local settings and start the application:

```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match '^(?<name>[^#][^=]*)=(?<value>.*)$') {
    Set-Item -Path "Env:$($matches.name)" -Value $matches.value
  }
}
uvicorn app.main:app --reload
```

9. Open http://127.0.0.1:8000 and upload `sample/synthetic-screenplay.pdf`.

## Part 4 - Create the public GitHub repository

1. Open https://github.com/new.
2. Enter repository name `script-sentinel`.
3. Set visibility to **Public**.
4. Do not add another README, license, or `.gitignore`; these already exist locally.
5. Select **Create repository**.
6. Copy the repository URL and send only that URL to Codex.

Before publishing, verify that `.env` is not listed among the files being uploaded.

## Part 5 - Deploy to Cloud Run

After the local test works, Codex can prepare and run the deployment command. Deployment will:

1. Build the container from the Dockerfile.
2. Store the Parallel key in Google Secret Manager.
3. Give the Cloud Run service permission to read that secret.
4. Deploy a public web service.
5. Return a URL ending in `run.app`.

Do not proceed to the demo video until the public URL works in a private/incognito browser window.

## Part 6 - Record the demo

1. Use the provided synthetic screenplay, not a commercial movie script.
2. Record the browser and narrate in English.
3. Show upload, processing, at least three findings, citations, and the architecture.
4. Keep the complete video under 3 minutes.
5. Upload to YouTube or Vimeo and make it publicly visible.
6. Do not include API keys, account pages, terminal secrets, third-party logos, or copyrighted footage/music.

## Part 7 - Submit on Devpost

1. Open your Devpost project.
2. Add the public Cloud Run URL.
3. Add the public repository URL.
4. Add the public YouTube/Vimeo URL.
5. Select the **Parallel** track.
6. Paste the prepared project description.
7. Verify the team list, English text, license visibility, and every URL.
8. Submit before the deadline and save a screenshot of the confirmation.

