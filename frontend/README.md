# TruthLens Frontend

React + TypeScript frontend for the TruthLens FastAPI backend.

## Run locally

1. Install dependencies:

```bash
npm install
```

2. Configure the backend URL:

```bash
cp .env.example .env
```

3. Start the frontend:

```bash
npm run dev
```

The app expects the FastAPI server in `backend_server/main.py` to be running on `http://127.0.0.1:8000` unless you override `VITE_API_BASE_URL`.

## Folder structure

- `src/app`: App entry composition
- `src/config`: Environment configuration
- `src/features/claim-verification`: API, hooks, page, and components for the main workflow
- `src/services`: Shared HTTP helpers
- `src/types`: Shared TypeScript models
- `src/styles`: Global styling
