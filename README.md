## SanchAI Weather

SanchAI Weather is a minimal full-stack demo that uses:

- **Frontend**: React + TypeScript (Vite) single-page chat UI
- **Backend**: FastAPI + LangChain-based agent
- **LLM**: OpenRouter (OpenAI-compatible API)
- **Tooling**: LangChain tool that calls Open-Meteo to fetch real current weather

You can ask both normal questions and weather-related questions. When you ask about the weather (even indirectly), the backend calls a **real weather API** and does **not** guess temperatures.

---

### Project Structure

- **`backend/`**: FastAPI app (`/chat` endpoint) + LangChain agent + weather tool.
- **`frontend/`**: Vite + React + TypeScript single-page chat UI.

---

### 1. Prerequisites

- **Python 3.10+** available as `python3`
- **Node.js** (LTS) + `npm`
- An **OpenRouter API key**

---

### 2. Configure Environment Variables (Backend)

Create a file `backend/.env` with:

```text
OPENROUTER_API_KEY=your_real_openrouter_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
APP_URL=http://localhost:5173
APP_NAME=SanchAI Weather
```

Explanation:

- **OPENROUTER_API_KEY**: Your OpenRouter key (required).
- **OPENROUTER_MODEL**: Model ID (defaults to `openai/gpt-4o-mini` if omitted).
- **APP_URL**: The URL where the frontend runs (used for CORS + OpenRouter headers).
- **APP_NAME**: A friendly name sent to OpenRouter in headers.

---

### 3. Run the Backend (FastAPI + LangChain)

In a terminal:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`.

**What it exposes**

- **POST `/chat`**
  - Request body: `{"message": "What is the weather of Pune?"}`
  - Response body: `{"answer": "Current weather for Pune, IN: 24°C, wind 8 km/h (as of 2025-12-15T10:30)."}`

Internally, the backend:

- Uses an LLM via **OpenRouter**.
- Detects if the question is **weather-related**; if so, it calls the `get_weather` tool.
- The tool uses **Open-Meteo** geocoding + forecast APIs and returns real current weather.

---

### 4. Run the Frontend (Vite + React)

Open a **second** terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and talks to the backend at `http://localhost:8000/chat`.

---

### 5. Using the App

1. Open `http://localhost:5173` in your browser.
2. Type a message in the input box and press **Enter** or click **Send**.
3. You will see:
   - Your **message** (role: user).
   - The **assistant answer** from the backend.
   - A **“Thinking…”** indicator while waiting for the backend.

**Example Prompts**

- **"What is the weather of Pune?"**
- **"weather in Delhi today"**
- **"Do I need a jacket in London?"**
- **"Do I need an umbrella in Mumbai today?"**
- **"Tell me a joke"**

Weather questions will trigger a real call to Open-Meteo; non-weather questions are answered directly by the LLM.

---

### 6. How Weather Tooling Works (Overview)

- The backend defines an async LangChain tool `get_weather(city: str)` in `app/tools/weather.py`.
- For a given city:
  - Calls **Open-Meteo Geocoding** to get latitude/longitude.
  - Calls **Open-Meteo Forecast** with `current_weather=true`, `temperature_unit=celsius`, `windspeed_unit=kmh`.
  - Returns a concise string such as:
    - `Current weather for Pune, IN: 24°C, wind 8 km/h (as of 2025-12-15T10:30).`
- If the city is unknown or an error happens, it returns a **friendly error message** instead of crashing.

---

### 7. Troubleshooting

- **CORS issues**
  - Ensure `APP_URL` in `backend/.env` is exactly the frontend origin (including port), e.g. `http://localhost:5173`.
  - Restart the backend after changing `.env`.

- **Missing `OPENROUTER_API_KEY`**
  - The backend will fail to start or will throw errors when calling the model.
  - Set `OPENROUTER_API_KEY` in `backend/.env` and restart the virtualenv and server.

- **500 error / “NetworkError when attempting to fetch resource” in frontend**
  - Check the backend terminal for stack traces.
  - Confirm:
    - `uvicorn app.main:app --reload --port 8000` is running without exceptions.
    - Your machine has network access to `https://openrouter.ai` and `https://api.open-meteo.com`.

- **Model not calling tools for weather questions**
  - The current agent logic:
    - Uses the LLM to decide if a message is about weather and extract a city.
    - If yes, it calls `get_weather` (which uses real data) and then has the LLM craft a final answer.
  - If tool calls seem wrong, restart the backend so it reloads the latest `agent.py`.

---

### 8. Quick Start (Shortest Version)

1. **Backend**

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

2. **Frontend**

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Use in browser**: open `http://localhost:5173` and ask  
   **"What is the weather of Pune?"**

