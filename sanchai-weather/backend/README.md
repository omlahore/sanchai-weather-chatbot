## Backend - SanchAI Weather

This is a minimal FastAPI backend that exposes a `/chat` endpoint backed by a LangChain agent using OpenRouter and a weather tool that calls Open-Meteo.

### Features

- **POST `/chat`**: Accepts JSON `{"message": string}` and returns `{"answer": string}`.
- **LangChain agent** using OpenRouter (`ChatOpenAI`) with a **tool-calling agent**.
- **Weather tool** using Open-Meteo geocoding + forecast APIs for real current weather.

### Setup

1. Create and activate a virtual environment:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in `backend/` based on `.env.example`:

```text
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
APP_URL=http://localhost:5173
APP_NAME=SanchAI Weather
```

### Run the Backend

```bash
uvicorn app.main:app --reload --port 8000
```

The server will be available at `http://localhost:8000`.

### Endpoint

- **POST `/chat`**
  - **Request body**: `{"message": "What is the weather of Pune?"}`
  - **Response body**: `{"answer": "Current weather for Pune, IN: ..."}`

### Troubleshooting

- **CORS errors**:
  - Ensure `APP_URL` matches the frontend origin (including port).
  - Restart the backend after changing `.env`.

- **Missing `OPENROUTER_API_KEY`**:
  - The backend may raise an error when building the agent.
  - Set the key in `.env` and restart the server.

- **Model not calling tools for weather**:
  - Confirm the system prompt in `agent.py` and that `get_weather` is included in the tools list.
  - Ensure you are using a **tool-calling agent** (`create_tool_calling_agent`) with the LangChain `AgentExecutor`.


