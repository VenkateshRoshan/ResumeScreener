import os
import sys
import json
from datetime import datetime

import judgeval
from judgeval.common.tracer import Tracer

from typing import Dict, Any, TypedDict, Optional

sys.path.append(os.getcwd())
from config import LLM_CONFIG, FILE_CONFIG, AGENT_CONFIG, JUDGEVAL_CONFIG

from Agents.jdParserAgent import JDParserAgent
from Agents.resumeParserAgent import ResumeParserAgent
from Agents.matcherAgent import MatcherAgent

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define state structure
class RMAState(TypedDict):
    """
    State for Resume Matching Agent
    """
    resume_file_path: str
    resume_text: str
    jd_text: str
    resume_data: Dict[str, Any]
    jd_data: Dict[str, Any]
    match_results: Dict[str, Any]
    final_report: str
    error: Optional[str] = None # If any error occurred b/w the process

def initialize_llm():
    model_name = LLM_CONFIG["model_name"]
    base_url = LLM_CONFIG["base_url"]

    if "llama" in model_name.lower() or "localhost" in base_url or "11434" in base_url:
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(model=model_name, base_url=base_url)
        print(f"Using Ollama model: {model_name}")
    else:
        from langchain_openai import OpenAI
        llm = OpenAI(model=model_name, api_key=os.getenv("OPENAI_API_KEY"))
        print(f"Using OpenAI model: {model_name}")
    return llm

llm = initialize_llm() # Initialize LLM

resume_agent = ResumeParserAgent(llm)
jd_agent = JDParserAgent(llm)
matcher_agent = MatcherAgent(llm)

tracer = Tracer() # can do this later

def create_workflow() -> StateGraph:
    """
        Create the LangGraph workflow
    """

    workflow = StateGraph(RMAState)

    # Add nodes
    workflow.add_node("parse_resume", parse_resume_node)
    workflow.add_node("parse_jd", parse_jd_node)
    workflow.add_node("match_analysis", match_analysis_node)
    workflow.add_node("compile_report", compile_report_node)

    # Define flow
    workflow.set_entry_point("parse_resume")

    workflow.add_edge("parse_resume", "parse_jd")
    workflow.add_edge("parse_jd", "match_analysis")
    workflow.add_edge("match_analysis", "compile_report")

    workflow.add_edge("compile_report", END)

    return workflow
    
@tracer.observe(name="resume_parsing_agent", span_type="resume")
def parse_resume_node(state: RMAState) -> RMAState:
    try:
        if state.get("resume_file_path"):
            resume_data = resume_agent.run(state["resume_file_path"])
        elif state.get("resume_text"):
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
                temp_file.write(state["resume_text"].encode("utf-8"))
                temp_file_path = temp_file.name
            
            resume_data = resume_agent.run(temp_file_path)

            # delete the temp file
            os.remove(temp_file_path)

        else:
            raise ValueError("No resume file or text provided")
        
        state["resume_data"] = resume_data
        logger.info("Resume parsed successfully")
        logger.info(f"Resume data: {resume_data}")

        # tracer.log(f"Resume data: {resume_data}")
        
    except Exception as e:
        logger.error(f"Error parsing resume: {e}")
        state["error"] = str(e)
        state["resume_data"] = {}

    return state

@tracer.observe(name="job_description_parsing_agent", span_type="job")
def parse_jd_node(state: RMAState) -> RMAState:
    try:
        logger.info("Parsing job description...")

        if not state.get("jd_text"):
            raise ValueError("No job description text provided")
        
        jd_data = jd_agent.run(state["jd_text"])
        state["jd_data"] = jd_data
        logger.info("Job description parsed successfully")
        logger.info(f"Job description data: {jd_data}")

    except Exception as e:
        logger.error(f"Error parsing job description: {e}")
        state["error"] = str(e)
        state["jd_data"] = {}

    return state

@tracer.observe(name="match_analysis_agent", span_type="match")
def match_analysis_node(state: RMAState) -> RMAState:
    try:
        logger.info("Analyzing match...")

        if not state.get("resume_data") or not state.get("jd_data"):
            raise ValueError("Missing resume or job description data")
        
        match_results = matcher_agent.run(state["resume_data"], state["jd_data"])
        state["match_results"] = match_results
        logger.info("Match analysis completed")

    except Exception as e:
        logger.error(f"Error during match analysis: {e}")
        state["error"] = str(e)
        state["match_results"] = {}

    return state

@tracer.observe(name="compile_report_node", span_type="report")
def compile_report_node(state: RMAState) -> RMAState:
    try:
        logger.info("Compiling report...")

        if state.get("error"):
            state["final_report"] = f"#Analysis Failed\n\nReason: {state['error']}"
            return state
        
        match_results = state["match_results"]
        resume_data = state["resume_data"]
        jd_data = state["jd_data"]

        final_report = f"""
            # Resume Analysis Report

            ## Match Score: {match_results.get("match_score", 0)}%

            ## Missing Skills: {len(match_results.get("missing_skills", []))}
            
                             : {', '.join(match_results.get('missing_skills', []))}

            ## Improvements: {chr(10).join([f'- {imp}' for imp in match_results.get('improvements', [])[:3]])}
        """

        state["final_report"] = final_report
        logger.info("Report compiled successfully")

    except Exception as e:
        logger.error(f"Error compiling report: {e}")
        state["error"] = str(e)
        state["final_report"] = ""

    return state

def process_resume_and_job(job_description=None, resume_file=None, resume_text=None, chat_history=None, user_message=""):
    """
        Afunction for both workflow processing
    """
    try:
        # Handle UI chat history
        if chat_history is not None:
            # UI mode
            if user_message.strip():
                response = "Follow-up questions not yet implemented."
                chat_history.append([user_message, response])
                return chat_history
            
            if not job_description or not job_description.strip():
                response = "Please provide a job description."
                chat_history.append(["Analysis", response])
                return chat_history
            
            if not resume_text and not resume_file:
                response = "Please provide a resume."
                chat_history.append(["Analysis", response])
                return chat_history
        
        # Get file path if uploaded
        resume_file_path = resume_file.name if resume_file else None
        
        # Create and run workflow
        workflow = create_workflow()
        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)
        
        initial_state = {
            "resume_file_path": resume_file_path,
            "resume_text": resume_text or "",
            "jd_text": job_description or "",
            "resume_data": {},
            "jd_data": {},
            "match_results": {},
            "final_report": "",
            "error": None
        }
        
        config = {"configurable": {"thread_id": "rma-analysis"}}
        result = app.invoke(initial_state, config)
        
        final_report = result.get("final_report", "No report generated")
        
        # Return based on mode
        if chat_history is not None:
            # UI mode
            chat_history.append(["Analysis Complete", final_report])
            return chat_history
        else:
            # Direct mode
            return result
            
    except Exception as e:
        if chat_history is not None:
            chat_history.append(["Error", f"Error: {str(e)}"])
            return chat_history
        else:
            return {"final_report": f"Error: {str(e)}", "error": str(e)}
        
if __name__ == "__main__":
    # Test with sample data
    test_jd = "Python developer with Django, React skills. 3+ years experience."
    test_resume_text = "I am a Python developer with 2 years Django experience."
    
    result = process_resume_and_job(
        job_description=test_jd,
        resume_text=test_resume_text
    )
    
    print(result["final_report"])