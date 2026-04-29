"""Run the PR Review Team on the sample repository."""

from dotenv import load_dotenv

load_dotenv()

from solution_graph import graph

print("PR Review Team — analyzing repository...\n")

result = graph.invoke({
    "pr_diff": "",
    "files_changed": [],
    "has_tests": False,
    "code_issues": [],
    "test_stubs": [],
    "standards_report": {},
    "final_report": "",
    "messages": [],
})

print("=" * 60)
print("FINAL PR REVIEW REPORT")
print("=" * 60)
print(result["final_report"])
