# Resume Match & Advisory Agent

This project helps job seekers quickly assess how well their resume aligns with a job description and offers actionable suggestions to improve it. It works by parsing your resume and a JD, comparing the content intelligently, and generating a clear, human-readable report.

Powered by LLMs and instrumented with [Judgeval](https://github.com/JudgmentLabs/judgeval) for agent-level evaluation.

## Features

- Upload or paste your `resume` and a `job description`
- Extracts structured data from job description and resume  
- Calculates a match score and identifies missing or extra skills  
- Suggests resume improvements and learning resources  
- Fully traceable using Judgeval for debugging and evaluation  
- Works with both FastAPI (backend) and Gradio (frontend)  

## Quick Start

### 1. Install requirements

```bash
pip install -r requirements.txt
```

### 2. Start your LLM backend

Make sure [Ollama](https://ollama.com) is installed and running:

```bash
ollama serve
ollama run llama3.1:8b
```

You can swap `llama3.1:8b` with any other model you prefer.

As of now this project supports OPENAI and OLLAMA models.

### 3. Run the backend API

```bash
python api.py
```

### 4. Launch the Gradio interface

In another terminal:

```bash
python app.py
```

You'll see a nice web UI at `http://localhost:7860`.

## Examples

You can test the pipeline using the examples provided:

```
examples/sample_resume.txt
examples/sample_jd.txt
```

Or upload your own `.pdf`, `.docx`, or `.txt` resume.

## Judgeval Integration

Each agent in the system is observed using `@tracer.observe()` and evaluated with Judgeval's `AnswerRelevancyScorer`. Traces are logged automatically during parsing and matching steps.

You'll find trace logs in your `~/.cache/judgeval` folder or wherever your Judgeval config points to.

## 🧪 Testing Individual Agents

Each agent is independently testable:

```bash
# Resume parsing
python Agents/resumeParserAgent.py --resume examples/sample_resume.txt

# Job description parsing
python Agents/jdParserAgent.py --jd examples/sample_jd.txt
```

## 📁 Project Structure

```
resumeScreener/
├── Agents/
│   ├── resumeParserAgent.py
│   ├── jdParserAgent.py
│   └── matcherAgent.py
├── api.py                    # FastAPI backend
├── app.py                    # Gradio frontend
├── main.py                   # LangGraph agent workflow
├── examples/                 # Sample test files
├── config.py                 # Model + path configs
requirements.txt
README.md
```

## Matching score Details
It's a weighted evaluation using:  
- Technical skills (30%)  
- Soft skills (15%)  
- Experience (25%)  
- Education (10%)  
- Domain relevance (10%)  
- Project impact (10%)

## ✅ To-Do (For Extension)

- More robust skill normalization  
- Dockerization (optional) 

## 🧠 Credits

Built as part of the Judgeval Agent Evaluation Challenge.    
Evaluation support from [Judgeval](https://github.com/judge-ai/judgeval).