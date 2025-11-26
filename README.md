- Study Buddy AI is a Streamlit-based learning companion that generates custom quizzes using Groq’s LLMs through LangChain. Users select a topic, difficulty, and question type, receive unique questions, attempt them in-app, and export their results for later review.

---

## Table of Contents
- [Architecture & Flow](#architecture--flow)
- [Core Features](#core-features)
- [Technology Stack](#technology-stack)
- [Local Development](#local-development)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Deployment](#deployment)
  - [Docker Image](#docker-image)
  - [Jenkins CI/CD](#jenkins-cicd-pipeline)
  - [Kubernetes & ArgoCD](#kubernetes--argocd)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## Architecture & Flow
1. **User Input (Streamlit UI)**  
   Topic, difficulty, question count, and type (MCQ or Fill in the Blank) are captured via sidebar controls in `app.py`.

2. **Question Generation**  
   `QuizManager.generate_questions()` orchestrates requests to `QuestionGenerator`. The generator assembles LangChain prompt templates (`src/prompts/templates.py`) and invokes Groq’s hosted LLM (`src/llm/groq_client.py`). Pydantic schemas (`src/models/question_schemas.py`) validate that responses follow the expected JSON contract.

3. **Quiz Attempt & Evaluation**  
   Questions render in the main Streamlit pane via `QuizManager.attempt_quiz()`. Upon submission, `QuizManager.evaluate_quiz()` compares user selections to model-provided answers, producing a pandas DataFrame.

4. **Results & Persistence**  
   Scores and per-question feedback are displayed inline. Users can export results as timestamped CSV files under `results/`.

---

## Core Features
- Topic-aware quiz generation with adjustable difficulty.
- MCQ and fill-in-the-blank formats with validation to ensure four MCQ options and proper blanks.
- Stateless Streamlit UI backed by session state for quiz lifecycle management.
- CSV export for analytics or record keeping.
- Rich logging via `src/common/logger.py` and custom exception handling.

---

## Technology Stack
- **Frontend/UI:** Streamlit 1.51
- **LLM Orchestration:** LangChain Core + LangChain Groq
- **Model Serving:** Groq Llama 3.1-8B
- **Data & Validation:** Pandas, Pydantic
- **Build & Packaging:** `pyproject.toml` (PEP 621), Python 3.13
- **Quality:** Ruff (linting)
- **Deployment:** Docker, Kubernetes, ArgoCD, Jenkins CI/CD

---

## Local Development

### Prerequisites
- Python ≥ 3.13
- Groq API key (see Environment Variables)

### Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

### Optional: Lint
```bash
ruff check .
```

---

## Environment Variables

| Variable       | Description                         | Required |
|----------------|-------------------------------------|----------|
| `GROQ_API_KEY` | API key for Groq LLM access         | Yes      |

- When running locally, place it in `.env` (loaded via `python-dotenv` in `app.py`).
- In Kubernetes, it is injected from the `groq-api-secret` Secret.

---

## Running the App
```bash
streamlit run app.py
```
- The app listens on `http://localhost:8501` by default.
- Streamlit session state keeps quiz progress per browser tab.

---

## Deployment

### Docker Image
The provided `Dockerfile`:
- Uses `python:3.13-slim`.
- Installs the project in editable mode.
- Exposes port `8501`.
- Starts Streamlit via `CMD ["streamlit", "run", "app.py", ...]`.

Build & run locally:
```bash
docker build -t study-buddy:local .
docker run -p 8501:8501 --env GROQ_API_KEY=your-key study-buddy:local
```

### Jenkins CI/CD Pipeline
`Jenkinsfile` stages:
1. **Checkout GitHub** – clones `main`.
2. **Build Docker Image** – `docker.build("${DOCKER_HUB_REPO}:${IMAGE_TAG}")`.
3. **Push Image** – authenticates with Docker Hub and pushes `andelataiwo/study-buddy:v${BUILD_NUMBER}`.
4. **Update Manifests** – `sed` replaces `__IMAGE_TAG__` in `manifests/deployment.yaml`.
5. **Commit YAML** – commits/pushes the tag change back to GitHub.
6. **Install kubectl & ArgoCD CLI** – ensures agents have required tooling.
7. **Apply & Sync** – logs into ArgoCD and runs `argocd app sync study`.

### Kubernetes & ArgoCD
- `manifests/deployment.yaml` defines a 2-replica Deployment in `argocd` namespace, pulling `andelataiwo/study-buddy:<tag>` and injecting `GROQ_API_KEY` from a Secret.
- `manifests/service.yaml` exposes the app as a NodePort Service mapping port 80 to container port 8501.
- ArgoCD watches the repo and syncs manifests after Jenkins pushes the updated image tag.

---

## Project Structure
```
.
├── app.py                 # Streamlit entrypoint
├── src/
│   ├── generator/question_generator.py
│   ├── prompts/templates.py
│   ├── utils/helpers.py   # QuizManager + UI helpers
│   ├── models/question_schemas.py
│   └── ...
├── results/               # Saved quiz CSVs
├── manifests/             # Kubernetes manifests
├── Jenkinsfile
├── Dockerfile
└── pyproject.toml
```

---

## Troubleshooting
- **Questions repeat:** ensure the prompt templates receive the latest `existing_questions` context so the LLM knows what to avoid.
- **LLM errors or empty questions:** confirm `GROQ_API_KEY` is set and quotas are available.
- **Streamlit session issues:** clear browser cache or stop/restart the app to reset `st.session_state`.
- **Kubernetes rollout stalls:** verify the Docker tag in `manifests/deployment.yaml` matches the pushed image and that ArgoCD sync succeeds (`argocd app sync study`).

---

Happy studying! 🎓

