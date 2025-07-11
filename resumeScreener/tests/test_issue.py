from dotenv import load_dotenv
load_dotenv()

from judgeval.common.tracer import Tracer

tracer = Tracer(project_name="resume_screening_agent")

@tracer.observe(name="test_log", span_type="debug")
def demo():
    tracer.log(label="testing_log", msg="log this")
    return "done"

print(demo())
