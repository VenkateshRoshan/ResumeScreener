"""

    Resume Parser Agent - This agent is responsible for parsing the resume and extracting the relevant information.

"""

import os
import json
from typing import Dict, List, Any, Optional

import sys
sys.path.append(os.getcwd())
from config import FILE_CONFIG

from dotenv import load_dotenv
load_dotenv()
from utils import initialize_llm

import PyPDF2
from docx import Document

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParserAgent:
    def __init__(self, llm):
        self.llm = llm

    def parse_resume(self, resume_file: str) -> Dict[str, Any]: # NOTE: Need to add the text limit length here
        """
        Parse the resume and extract the relevant information.
        """
        if resume_file is None:
            raise ValueError("Resume file is required")
        
        possible_extensions = FILE_CONFIG["supported_formats"]
        # extensions are not in possible_extensions
        if not resume_file.endswith(tuple(possible_extensions)):
            raise ValueError("Invalid file extension")
        
        if resume_file.endswith(".pdf"):
            try:
                with open(resume_file, "rb") as file:
                        
                    pdf_reader = PyPDF2.PdfReader(file, strict=False)  # Add strict=False
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    resume_text = text
            except Exception as e:
                logger.error(f"PDF parsing failed: {e}")
                resume_text = f"Error reading PDF: {str(e)}"
        elif resume_file.endswith(".docx"):
            # read the docx file
            doc = Document(resume_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            resume_text = text
        elif resume_file.endswith(".txt"):
            # read the txt file
            with open(resume_file, "r", encoding="utf-8") as file:
                resume_text = file.read()

        return resume_text
    
    def __parse_response__(self, resume_text: str) -> Dict[str, Any]:
        """
            Parse the response fromt the LLM.
        """
        try:
            prompt = f"""
                You are a resume extraction engine. Extract the following fields from the given resume text and return only a valid JSON object. No extra text, markdown, or code blocks.

                Required JSON structure:
                {{
                    "name": string,
                    "email": string,
                    "phone": string,
                    "linkedin": string,
                    "github": string,
                    "portfolio url": string,
                    "education": list of strings (only institution names and degrees),
                    "experience": list of objects with keys "company", "title", "location", "description", and "years of experience",
                    "skills": list of strings (extract all mentioned skills from the text),
                    "projects": list of strings or short descriptions,
                    "certifications": list of strings,
                    "publications": list of strings,
                    "awards": list of strings,
                    "summary": 2–3 sentence string,
                    "other": string or list (for miscellaneous information)
                }}

                Important Instructions:
                - If a field is not found, return the string "N/A" (not null or empty).
                - Output must be a single valid JSON object, without markdown, comments, or explanation.
                - Every value in the JSON object must be a string.
                - The input resume text is:
                {resume_text}
            """

            response = self.llm.invoke(prompt)

            # Clean the response - remove any markdown or extra text
            cleaned_response = response.content.strip() if hasattr(response, 'content') else response.strip()
            
            # logger.info(f"RAW LLM RESPONSE (RESUME PARSER) : {cleaned_response}")
            
            # Find JSON in response (in case LLM adds extra text)
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = cleaned_response[start_idx:end_idx]
                parsed_data = json.loads(json_str)

                return {
                    "name": parsed_data.get("name", "N/A"),
                    "email": parsed_data.get("email", "N/A"),
                    "phone": parsed_data.get("phone", "N/A"),
                    "linkedin": parsed_data.get("linkedin", "N/A"),
                    "github": parsed_data.get("github", "N/A"),
                    "portfolio url": parsed_data.get("portfolio url", "N/A"),
                    "education": parsed_data.get("education", "N/A"),
                    "experience": parsed_data.get("experience", "N/A"),
                    "skills": parsed_data.get("skills", "N/A"),
                    "projects": parsed_data.get("projects", "N/A"),
                    "certifications": parsed_data.get("certifications", "N/A"),
                    "publications": parsed_data.get("publications", "N/A"),
                    "awards": parsed_data.get("awards", "N/A"),
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
        except Exception as e:
            print(f"Error: {e}")
            return self.__get_default_response__()
            
    def __get_default_response__(self) -> Dict[str, Any]:
        """
            Get the default response from the LLM.
        """
        return {
            "name": "N/A",
            "email": "N/A",
            "phone": "N/A",
            "linkedin": "N/A",
            "github": "N/A",
            "portfolio url": "N/A",
            "education": "N/A",
            "experience": "N/A",
            "skills": "N/A",
            "projects": "N/A",
            "certifications": "N/A",
            "publications": "N/A",
            "awards": "N/A",
            "summary": "N/A",
            "other": "N/A"
        }
    
    def run(self, resume_file: str) -> Dict[str, Any]:
        """
            Run the resume parser agent.
        """
        logger.info(f"Parsing resume: {resume_file}")
        resume_text = self.parse_resume(resume_file)

        logger.info(f"Resume text")
        return self.__parse_response__(resume_text)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", "-r", type=str, required=True, help="Path to the resume file")
    args = parser.parse_args()

    llm = initialize_llm()
    agent = ResumeParserAgent(llm)
    result = agent.run(args.resume)
    print(result)