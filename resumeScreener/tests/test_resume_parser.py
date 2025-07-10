import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from Agents.resumeParserAgent import ResumeParserAgent
from main import initialize_llm

def test_resume_parser():
    llm = initialize_llm()
    agent = ResumeParserAgent(llm)
    result = agent.run("examples/sample_resume.txt")
    print(result)
    assert isinstance(result, dict)
    assert "skills" in result

test_resume_parser()