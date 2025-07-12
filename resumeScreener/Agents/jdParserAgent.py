"""
    JD Parse Agent - Parse the job description and extract the relevant information.
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


class JDParserAgent:
    def __init__(self, llm):
        self.llm = llm

    def parse_job_description(self, jd_text: str) -> Dict[str, Any]:
        """
            Parse the job description and extract the relevant information.
        """
        if jd_text is None:
            raise ValueError("Job description text is required")
        
        return jd_text.strip()
    
    def __parse_response__(self, jd_text: str) -> Dict[str, Any]:
        """
            Parse the response from the LLM.
        """
        try:
            prompt = f"""
                You are a job description parsing engine.

                Extract the following fields from the given job description and return a valid JSON object only. Do not include any explanations, text, markdown, or formatting—only the raw JSON.

                Extract the following structured fields from the job description below. 
                If a field is not explicitly stated, make a best guess based on context.
                Return only a valid JSON object with the following keys. No other text.

                Return the following fields:
                {{
                    "title": job title,
                    "company": company name,
                    "location": job location,
                    "type": full time, part time, contract, internship, etc.,
                    "experience required": minimum experience required in number of years ( should be a string ),
                    "qualifications": list of educational qualifications,
                    "required skills": list of skills required for the job,
                    "preferred skills": list of skills preferred for the job,
                    "salary": salary range,
                    "work type": remote, hybrid, on-site, etc.,
                    "summary": 2-3 sentence summary of the job,
                    "other": any other relevant information
                }}

                Job description:
                {jd_text}

                Respond ONLY with a valid JSON object. No extra text.
            """

            response = self.llm.invoke(prompt)

            # Clean the response - remove any markdown or extra text
            cleaned_response = response.content.strip() if hasattr(response, 'content') else response.strip()

            # logger.info(f"RAW LLM RESPONSE (JD PARSER) : {cleaned_response}")
            
            # Find JSON in response (in case LLM adds extra text) - cause json is a dict so extracting indices of '{' and '}' from the string.
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = cleaned_response[start_idx:end_idx]
                parsed_data = json.loads(json_str)

                return {
                    "title": parsed_data.get("title", "N/A"),
                    "company": parsed_data.get("company", "N/A"),
                    "location": parsed_data.get("location", "N/A"),
                    "type": parsed_data.get("type", "N/A"),
                    "experience required": parsed_data.get("experience required", "N/A"),
                    "qualifications": parsed_data.get("qualifications", "N/A"),
                    "required skills": parsed_data.get("required skills", "N/A"),
                    "preferred skills": parsed_data.get("preferred skills", "N/A"),
                    "salary": parsed_data.get("salary", "N/A"),
                    "work type": parsed_data.get("work type", "N/A"),
                    "summary": parsed_data.get("summary", "N/A"),
                    "other": parsed_data.get("other", "N/A")
                }
            else:
                raise ValueError("Invalid JSON response")
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print('--------------------------------')
            print(f"Response: {response}")
            print('--------------------------------')
            
            return self.__get_default_response__()
        
    def __get_default_response__(self) -> Dict[str, Any]:
        """
            Get the default response from the LLM.
        """
        return {
            "title": "N/A",
            "company": "N/A",
            "location": "N/A",
            "type": "N/A",
            "experience required": "N/A",
            "qualifications": "N/A",
            "required skills": "N/A",
            "preferred skills": "N/A",
            "salary": "N/A",
            "work type": "N/A",
            "summary": "N/A",
            "other": "N/A"
        }
    
    def run(self, jd_text: str) -> Dict[str, Any]:
        """
            Run the JD parser agent.
        """
        logger.info(f"Parsing job description")
        jd_text = self.parse_job_description(jd_text)
        return self.__parse_response__(jd_text)
        

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--jd", "-r", type=str, required=True, help="Path to the resume file")
    args = parser.parse_args()

    llm = initialize_llm()
    agent = JDParserAgent(llm)
    result = agent.run(args.jd)
    print(result)