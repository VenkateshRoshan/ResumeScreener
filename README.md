# Resume Match & Advisory Agent

This project helps job seekers quickly assess how well their resume aligns with a job description and offers actionable suggestions to improve it. It works by parsing your resume and a JD, comparing the content intelligently, and generating a clear, human-readable report.

Powered by LLMs and instrumented with [Judgeval](https://github.com/JudgmentLabs/judgeval) for agent-level evaluation.

## Features

* Upload or paste your `resume` and a `job description`
* Extracts structured data from job description and resume
* Calculates a match score and identifies missing or extra skills
* Suggests resume improvements and learning resources
* Fully traceable using Judgeval for debugging and evaluation
* Works with both FastAPI (backend) and Gradio (frontend)

## Prerequisites

* Python 3.10+
* [Ollama](https://ollama.com) installed and running (if using Ollama)
* Docker installed on your system (optional, for containerized deployment)

## LLM Configuration

The system supports both **Ollama** (local) and **OpenAI** models with automatic provider detection:

### Ollama Setup (Local Models)
```bash
# .env configuration
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
LLM_BASE_URL=http://localhost:11434
```

### OpenAI Setup (Cloud Models)
```bash
# .env configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
LLM_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-your_openai_api_key_here
```

The system automatically detects which provider to use based on the `LLM_PROVIDER` environment variable. Simply change this value to switch between local Ollama models and OpenAI's cloud models without any code modifications.

## Quick Start

**Choose one method:**
- **Local Python setup** (see below)
- **Docker setup** (see Docker Setup section)

### Local Python Setup

#### 1. Install requirements

```bash
pip install -r requirements.txt
```

#### 2. Start your LLM backend

**For Ollama (Recommended):**
```bash
# Terminal 1: Start Ollama server
ollama serve

# Terminal 2: Load your model
ollama run llama3.1:8b
```

You can swap `llama3.1:8b` with any other model you prefer.

As of now this project supports **OpenAI** and **Ollama** models.

#### 3. Create environment file

Create a `.env` file in the `resumeScreener/` directory with your configuration:

```bash
# Judgeval Configuration
JUDGMENT_API_KEY=your_judgeval_api_key_here
JUDGMENT_ORG_ID=your_judgeval_org_id_here

# OLLAMA Configuration (Default)
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
LLM_BASE_URL=http://localhost:11434

# OpenAI Configuration (Alternative - uncomment to use)
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4
# LLM_BASE_URL=https://api.openai.com/v1
# OPENAI_API_KEY=sk-your_openai_api_key_here
```

#### 4. Run the backend API

```bash
python resumeScreener/api.py
```

#### 5. Launch the Gradio interface

In another terminal:

```bash
python resumeScreener/app.py
```

You'll see a nice web UI at `http://localhost:7860`.

## Docker Setup

### 1. Build the Docker image

```bash
docker build -t resume-rma .
```

### 2. Start Ollama on your host

```bash
# Terminal 1: Start Ollama server
ollama serve

# Terminal 2: Load your model
ollama run llama3.1:8b
```

### 3. Create environment file

Create a `.env` file in the `resumeScreener/` directory with your API keys:

```bash
# Judgeval Configuration
JUDGMENT_API_KEY=your_judgeval_api_key_here
JUDGMENT_ORG_ID=your_judgeval_org_id_here

# OLLAMA Configuration
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
LLM_BASE_URL=http://localhost:11434

# OpenAI Configuration (only if using OpenAI)
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4
# LLM_BASE_URL=https://api.openai.com/v1
# OPENAI_API_KEY=sk-your_openai_api_key_here
```

### 4. Run with Docker

```bash
docker run --env-file resumeScreener/.env \
  -e LLM_BASE_URL=http://localhost:11434 \
  --network=host \
  resume-rma
```

### Access the application

* **Gradio UI:** http://localhost:7860
* **FastAPI docs:** http://localhost:8000/docs

### Docker Notes

* Using `--network=host` allows the container to connect to your locally running Ollama
* The `--env-file` flag loads all environment variables from your `.env` file
* API keys are kept secure and never baked into the Docker image
* On Linux: `--network=host` is recommended for best performance
* On Windows/Mac: May need to use `host.docker.internal` instead of `localhost`

## Examples

You can test the pipeline using the examples provided:

```bash
examples/sample_resume.txt
examples/sample_jd.txt
```

Or upload your own `.pdf`, `.docx`, or `.txt` resume through the web interface.

## Usage

1. **Upload Resume:** Choose a file or paste resume text
2. **Add Job Description:** Paste the job description or provide a URL
3. **Analyze:** Click "Analyze Match" to process
4. **Review Results:** Get match score, missing skills, and improvement suggestions
5. **Download Report:** Save the generated report as Markdown

## Judgeval Integration

Each agent in the system is observed using `@tracer.observe()` and evaluated with Judgeval's scoring mechanisms. Traces are logged automatically during parsing and matching steps.

You'll find trace logs in your `~/.cache/judgeval` folder or wherever your Judgeval config points to.

**Trace Links:** Click the "🔍 View Trace" links in the application to see detailed execution traces.

## 🧪 Testing Individual Agents

Each agent is independently testable:

```bash
# Resume parsing
python Agents/resumeParserAgent.py --resume examples/sample_resume.txt

# Job description parsing
python Agents/jdParserAgent.py --jd examples/sample_jd.txt

# Full pipeline test
python resumeScreener/main.py --resume examples/sample_resume.txt --jd examples/sample_jd.txt
```

## 📁 Project Structure

```
ResumeScreener/
├── resumeScreener/
│   ├── Agents/
│   │   ├── __init__.py
│   │   ├── resumeParserAgent.py    # Resume parsing agent
│   │   ├── jdParserAgent.py        # Job description parsing agent
│   │   ├── matcherAgent.py         # Matching & scoring agent
│   │   └── advisorAgent.py         # Advisory & recommendation agent
│   ├── api.py                      # FastAPI backend
│   ├── app.py                      # Gradio frontend
│   ├── main.py                     # LangGraph agent workflow
│   ├── config.py                   # Model + path configs
│   └── .env                        # Environment variables
├── examples/                       # Sample test files
│   ├── sample_resume.txt
│   └── sample_jd.txt
├── reports/                        # Generated reports
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

## API Endpoints

### FastAPI Backend (`http://localhost:8000`)

* `POST /analyze` - Analyze resume against job description
* `GET /health` - Health check endpoint
* `GET /docs` - Interactive API documentation

### Request Format

```json
{
  "resume_text": "Your resume content...",
  "jd_text": "Job description content...",
  "resume_file": "base64_encoded_file_optional"
}
```

### Response Format

```json
{
  "match_score": 85,
  "matching_skills": ["Python", "SQL", "Machine Learning"],
  "missing_skills": ["Docker", "Kubernetes"],
  "improvements": ["Add more quantified achievements", "..."],
  "final_report": "# Resume Analysis Report\n...",
  "error": null
}
```

## Matching Score Details

The match score is calculated using a weighted evaluation:

* **Technical skills** (30%) - Programming languages, tools, frameworks
* **Experience** (25%) - Years of experience, role relevance
* **Soft skills** (15%) - Communication, leadership, teamwork
* **Education** (10%) - Degree relevance, certifications
* **Domain relevance** (10%) - Industry/domain experience
* **Project impact** (10%) - Quantified achievements, project scope

**Score Ranges:**
* 90-100%: Excellent match
* 75-89%: Good match
* 60-74%: Moderate match
* Below 60%: Needs improvement

## Troubleshooting

### Common Issues

**1. Connection Refused Error:**
```bash
# Ensure Ollama is running
ollama serve

# Check if model is loaded
ollama list
```

**2. Docker Network Issues:**
```bash
# For Linux, use host network
docker run --network=host ...

# For Windows/Mac, use bridge network
docker run -p 7860:7860 -p 8000:8000 ...
```

**3. Missing Dependencies:**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

**4. Judgeval Traces Not Showing:**
```bash
# Check Judgeval configuration
export JUDGMENT_API_KEY=your_key
export JUDGMENT_ORG_ID=your_org_id
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LLM_PROVIDER` | LLM provider (ollama/openai) | ollama | Yes |
| `LLM_MODEL` | Model name | llama3.1:8b | Yes |
| `LLM_BASE_URL` | LLM API endpoint | http://localhost:11434 | Yes |
| `JUDGMENT_API_KEY` | Judgeval API key | - | Yes |
| `JUDGMENT_ORG_ID` | Judgeval organization ID | - | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | If using OpenAI |

### Model Support

**Ollama Models (Tested):**
* llama3.1:8b (recommended)
* llama2:7b

**OpenAI Models (Tested):**
* gpt-4
* gpt-3.5-turbo
* gpt-4-turbo

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ✅ To-Do (For Extension)

* [ ] Adding Question & Answer support
* [ ] More robust skill normalization
* [ ] Resume template suggestions
* [ ] ATS-friendly resume formatting recommendations

## 🧠 Credits

Built as part of the **Judgeval Agent Evaluation Challenge**.

* **Evaluation Framework:** [Judgeval](https://github.com/judge-ai/judgeval)
* **LLM Integration:** [Ollama](https://ollama.com) & [OpenAI](https://openai.com)
* **Web Framework:** [FastAPI](https://fastapi.tiangolo.com) & [Gradio](https://gradio.app)
* **Agent Orchestration:** [LangGraph](https://langchain-ai.github.io/langgraph/)

## Support

* 📖 **Documentation:** [Judgeval Docs](https://docs.judgmentlabs.ai/documentation)

---