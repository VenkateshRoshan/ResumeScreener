import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from Agents.matcherAgent import MatcherAgent
from main import initialize_llm

def test_matcher_agent():
    llm = initialize_llm()
    agent = MatcherAgent(llm)
    result = agent.run("examples/sample_jd.txt", "examples/sample_resume.txt")
    print(result)

test_matcher_agent()