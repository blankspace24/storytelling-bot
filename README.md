#  StoryLens — AI-Powered Script Analysis Platform

StoryLens is an end-to-end **AI-powered storytelling intelligence system** that analyzes scripts using **LLMs (Mistral AI)** and provides structured insights like emotional arcs, engagement scores, and improvement suggestions.

Built with a modern stack:

*  FastAPI (async backend)
*  LangChain (LLM orchestration)
*  Mistral AI (LLM provider)
*  Streamlit (interactive frontend)

---

##  Features

### AI-Powered Analysis

* Uses **Mistral Large Model**
* Structured output via **LangChain JSON parser**
* Prompt-engineered for storytelling insights

###  Rich Insights

* Story summary
* Emotional arc (with visualization)
* Engagement score (0–100)
* Factor-wise breakdown
* Actionable improvement suggestions
* Cliffhanger detection

###  Scalable Backend

* Fully async FastAPI
* Retry with exponential backoff
* Strong schema validation via Pydantic

###  Interactive UI

* Streamlit dashboard
* Plotly visualizations
* Clean modern UI (glassmorphism style)

---

##  System Design

###  High-Level Architecture

```
          ┌────────────────────┐
          │   Streamlit UI     │
          │ (Frontend Client)  │
          └─────────┬──────────┘
                    │ HTTP (REST)
                    ▼
          ┌────────────────────┐
          │    FastAPI Server  │
          │  (Async Backend)   │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │  Script Analyzer   │
          │ (LangChain LCEL)   │
          └─────────┬──────────┘
                    │
        ┌───────────▼───────────┐
        │ Prompt → LLM → Parser │
        │  (LangChain Chain)    │
        └───────────┬───────────┘
                    │
                    ▼
          ┌────────────────────┐
          │   Mistral AI API   │
          │   (LLM Provider)   │
          └────────────────────┘
```

---

### 🔹 Component Breakdown

####  Frontend (Streamlit)

* Collects script input
* Calls backend `/api/analyze`
* Displays charts and insights

####  Backend (FastAPI)

* Async request handling
* Input validation
* Error handling
* LLM orchestration trigger

####  Analyzer (LangChain)

Pipeline:

```
Prompt Template → Mistral LLM → JSON Parser
```

#### 🤖 LLM Provider (Mistral AI)

* Model: `mistral-large-latest`
* Performs reasoning, scoring, and analysis

---

### 🔹 Request Flow

```
User Input → Streamlit UI
           → FastAPI (/api/analyze)
           → ScriptAnalyzer
           → LangChain Chain (ainvoke)
           → Mistral API
           → JSON Response
           → Pydantic Validation
           → UI Rendering
```

---

### 🔹 Async & Retry Design

* Fully async pipeline (`async/await`)
* Non-blocking LLM calls
* Retry strategy:

```
1s → 2s → 4s (exponential backoff)
```

---

### 🔹 Data Flow

```
Script Input
   ↓
Prompt Engineering
   ↓
LLM Processing
   ↓
Structured JSON
   ↓
Validation (Pydantic)
   ↓
Frontend Visualization
```

---

### 🔹 Scalability (Future Ready)

* Add Redis caching
* Introduce queue (Celery / Kafka)
* Horizontal scaling with containers
* API Gateway for rate limiting

---

## 📁 Project Structure

```
story_telling/
│
├── backend/
│   ├── analyzer.py
│   ├── main.py
│   ├── models.py
│   └── prompts.py
│
├── config/
│   └── settings.py
│
├── streamlit/
│   └── app.py
│
├── outputimage/
│   ├── s1.png
│   ├── s2.png
│   ├── s3.png
│   ├── s4.png
│   └── s5.png
├── .env
├── requirements.txt
├── start.bat
├── start.sh
└── README.md
```

---

##  Setup Instructions

### 1️⃣ Clone Repository

```
git clone https://github.com/blankspace24/storytelling-bot.git
cd story_telling
```

### 2️⃣ Create Virtual Environment

```
python -m venv env
```

Activate:

* Windows: `env\Scripts\activate`
* Linux/Mac: `source env/bin/activate`

---

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

### 4️ Environment Variables

Create `.env` file:

```
MISTRAL_API_KEY=your_api_key

API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://localhost:8000

DEFAULT_MODEL=mistral-large-latest
LLM_TEMPERATURE=0.7
LLM_MAX_RETRIES=3
```

---

##  Running the Application

### Start Backend

```
uvicorn backend.main:app --reload --port 8000
```

### Start Frontend

```
streamlit run streamlit/app.py
```

---

##  API Endpoints

###  Analyze Script

```
POST /api/analyze
```

Request:

```json
{
  "title": "My Script",
  "script_text": "Your script here..."
}
```

---

###  Health Check

```
GET /api/health
```

---

##  Core Technologies

* FastAPI
* LangChain
* Mistral AI
* Streamlit
* Plotly
* Pydantic
* Asyncio

---

##  Error Handling

* 400 → Invalid input
* 500 → Server error
* 502 → LLM failure
* Retry mechanism ensures resilience

---

##  Future Improvements

* Multi-LLM support (OpenAI, Claude)
* Script genre detection
* User authentication
* Save history
* Batch processing

---

##  Author

** Somana Naga Venkata Siva Gopi **
AI Engineer | Generative AI | LLM Systems

---

##  Why This Project Matters

This project demonstrates:

* Real-world **LLM system design**
* Async scalable backend
* Structured AI outputs
* End-to-end product thinking


