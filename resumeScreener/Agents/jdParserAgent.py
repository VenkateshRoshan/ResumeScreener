"""
    JD Parse Agent - Parse the job description and extract the relevant information.
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
                Extract the following information from the job description:
                {{
                    "title": job title,
                    "company": company name,
                    "location": job location,
                    "type": full time, part time, contract, internship, etc.
                    "experience required": minimum experience required in number of years,
                    "qualifications": list of educational qualifications,
                    "required skills": list of skills required for the job,
                    "preferred skills": list of skills preferred for the job,
                    "salary": salary range,
                    "work type": remote, hybrid, on-site, etc.
                    "summary": summary of the job description in 2-3 sentences briefly,
                    "other": other information
                }}
                The response should be in JSON format.
                If you cannot find the information, return "" value for the respective key. You have to remember you have to return a string not a null value.
                The job description is:
                {jd_text}.
                You have to return Clean JSON response No other text or markdown.
            """
            response = self.llm.invoke(prompt)
            
            # logger.info(f"RAW LLM RESPONSE (JD PARSER) : {response}")

            # Clean the response - remove any markdown or extra text
            cleaned_response = response.strip()
            
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
    def initialize_llm():
        model_name = LLM_CONFIG["model_name"]
        base_url = LLM_CONFIG["base_url"]

        print(f"Using model: {model_name} and base url: {base_url}")

        if "ollama" in model_name.lower() or "llama" in model_name.lower():
            # use ollama
            from langchain_ollama import OllamaLLM
            llm = OllamaLLM(model=model_name, base_url=base_url)
        else:
            # use openai
            from langchain_openai import OpenAI
            llm = OpenAI(model=model_name, api_key=os.getenv("OPENAI_API_KEY"))
        return llm
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--jd", "-r", type=str, required=True, help="Path to the resume file")
    args = parser.parse_args()

    llm = initialize_llm()
    agent = JDParserAgent(llm)
    result = agent.run(args.jd)
    print(result)