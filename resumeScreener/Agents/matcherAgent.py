"""
    Matcher Agent - Match the resume with the job description.
"""

import os
import json
from typing import Dict, List, Any, Optional

import sys
sys.path.append(os.getcwd())
from config import LLM_CONFIG, FILE_CONFIG

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatcherAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def run(self, resume_json: Dict, jd_json: Dict) -> Dict[str, Any]:
        """
        Complete matching analysis in one LLM call.
        """
        try:
            prompt = f"""
                You are an expert recruiter. Compare the resume and job description:
                {{
                    "match_score": a value, # TODO: need to add more matching score criteria like technical, soft skills, experience, education, etc.
                    "missing_skills": ["skill1", "skill2"],
                    "matching_skills": ["skill3", "skill4"],
                    "improvements": ["what to improve", "what to add", "what to remove"],
                    "where_to_improve": ["which sections to focus"],
                }}
                
                Resume: {json.dumps(resume_json)}
                Job: {json.dumps(jd_json)}

                Return only valid JSON and no other text.
                - match_score       : integer from 0 to 100 value only add % at the end of the score.
                - missing_skills    : list of skills mentioned in the job but not in the resume.
                - matching_skills   : list of skills present in both the resume and the job description.
                - improvements      : list of 3 actionable suggestions to improve the resume.
                - where_to_improve  : list of resume sections or areas to focus on.
                You just have to return JSON no code block or text or anything else.
            """
            
            response = self.llm.invoke(prompt)

            logger.info(f"RAW LLM RESPONSE (MATCHER AGENT) : {response}")

            # Clean and parse JSON response
            cleaned_response = response.strip()
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = cleaned_response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            print(f"Error in matching: {e}")
            return {
                "match_score": 0.0,
                "missing_skills": [],
                "matching_skills": [],
                "improvements": [],
                "where_to_improve": []
            }
    
if __name__ == "__main__":
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
    
    # Test with sample data
    llm = initialize_llm()
    agent = MatcherAgent(llm)
    
    sample_resume = {
        "skills": ["Python", "Django", "SQL"],
        "experience_years": 3,
        "education": ["Bachelor's in CS"]
    }
    
    sample_jd = {
        "required_skills": ["Python", "Django", "React"],
        "experience_required": 2,
        "education_required": ["Bachelor's degree"]
    }
    
    result = agent.run(sample_resume, sample_jd)
    print(result)