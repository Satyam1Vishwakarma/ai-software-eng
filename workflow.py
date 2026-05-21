from typing import TypedDict
from langgraph.graph import StateGraph, END

from agents.planner import planner_node
from agents.coder import coder_node
from agents.reviewer import reviewer_node


class AgentState(TypedDict):
    user_request: str
    plan: str
    code_result: str
    review: str
    approved: bool


def review_decision(state: AgentState):

    if state["approved"]:
        return END

    return "coder"


graph = StateGraph(AgentState)

graph.add_node("planner", planner_node)
graph.add_node("coder", coder_node)
graph.add_node("reviewer", reviewer_node)
graph.set_entry_point("planner")

graph.add_edge("planner", "coder")
graph.add_edge("coder", "reviewer")
graph.add_conditional_edges(
    "reviewer",
    review_decision
)

app = graph.compile()

i=input("User:")

result = app.invoke({
    "user_request": i
})

print(result)