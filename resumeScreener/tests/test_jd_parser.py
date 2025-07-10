import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from Agents.jdParserAgent import JDParserAgent
from main import initialize_llm

def test_jd_parser():
    llm = initialize_llm()
    agent = JDParserAgent(llm)
    result = agent.run("examples/sample_jd.txt")
    print(result)

test_jd_parser()