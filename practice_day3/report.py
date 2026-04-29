"""Report Assembler — compiles output from all agents into a final report."""

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langsmith import traceable

from config import LLM_MODEL
from lib.prompts import REPORT_PROMPT


@traceable(name="Report Assembler")
def assemble_report(state):
    """Collect all agent results and generate the final PR report."""
    code_issues = state.get("code_issues", [])
    test_stubs = state.get("test_stubs", [])
    standards_report = state.get("standards_report", {})
    files_changed = state.get("files_changed", [])

    context = f"""Files changed: {files_changed}

Code Issues:
{code_issues}

Generated Tests:
{test_stubs}

Standards Review:
{standards_report}"""

    llm = ChatOpenAI(model=LLM_MODEL)
    result = llm.invoke([
        SystemMessage(content=REPORT_PROMPT),
        {"role": "user", "content": f"Compile this into a final PR Review Report:\n\n{context}"},
    ])

    return {"final_report": result.content}
