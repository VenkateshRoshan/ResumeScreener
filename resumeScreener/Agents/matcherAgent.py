"""
    Matcher Agent - Match the resume with the job description.
"""

import os
import json
from typing import Dict, List, Any, Optional

from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.append(os.getcwd())
from config import FILE_CONFIG
from utils import initialize_llm
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
                You are a highly skilled technical recruiter. Carefully analyze and compare the following resume and job description, both provided as structured JSON.

                Your task is to evaluate how well the candidate fits the job based on the following criteria and return a detailed JSON object with the evaluation.

                Scoring Criteria:
                - "match_score": Overall resume-to-job fit, integer from 0 to 100, based on a weighted combination of:
                    - Technical skill match (30%)
                    - Soft skill match (15%)
                    - Relevant experience (25%)
                    - Education alignment (10%)
                    - Domain or industry relevance (10%)
                    - Project relevance or impact (10%)

                Suggestions:
                - Provide specific suggestions for improvements in the resume
                - Suggest additional skills that the candidate might need to develop
                - Suggest ways to highlight relevant experience
                - Suggest ways to align education with the job requirements
                - Suggest ways to match the candidate's skills to the job description
                - Follow ATS best practices and format the resume accordingly

                Matching Skills:
                - Provide a list of skills that are found in both the resume and the job description

                Missing Skills:
                - Provide a list of skills that are required by the job but missing in the resume

                Feedback Structure:
                {{
                    "match_score": integer,  // final score from 0 to 100
                    "matching_skills": ["skill1", "skill2"],  // skills found in both resume and job description
                    "missing_skills": ["skill3", "skill4"],   // skills required by the job but missing in the resume
                    "Suggestions": [
                        "suggestion1",
                        "suggestion2",
                        "suggestion3",
                    ]
                }}

                Resume JSON:
                {json.dumps(resume_json)}

                Job Description JSON:
                {json.dumps(jd_json)}

                Instructions:
                - Return ONLY a valid JSON object as specified, do not add any other text or markdown and do not forget to add at the end of the JSON object.
                - Do not include explanations, markdown formatting, or any additional text.
                Do not return any other text at all , return JSON object only.
            """
            
            response = self.llm.invoke(prompt)

            # logger.info(f"RAW LLM RESPONSE (MATCHER AGENT) : {response}")

            # Clean and parse JSON response
            cleaned_response = response.content.strip() if hasattr(response, 'content') else response.strip()
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = cleaned_response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            print(f"Error in matching: {e}")
            print('--------------------------------')
            print(f"Response: {response}")
            print('--------------------------------')
            
            return {
                "match_score": 0.0,
                "missing_skills": [],
                "matching_skills": [],
                "Suggestions": []
            }
    
if __name__ == "__main__":
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