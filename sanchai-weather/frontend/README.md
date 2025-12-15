## Frontend - SanchAI Weather

This is a minimal React + TypeScript single-page app built with Vite. It provides:

- **Chat-style UI** with message history
- **Single input field + Send button**
- Integration with the FastAPI backend `/chat` endpoint

### Setup

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173` in your browser.

The app expects the backend to be running at `http://localhost:8000`.

### Usage

Type a message and press **Enter** or click **Send**. The conversation history appears above the input box, with a small “Thinking…” indicator while the backend is working.

Example prompts:

- `What is the weather of Pune?`
- `weather in Delhi today`
- `Do I need a jacket in London?`


