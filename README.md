**Project Overview**

- **Description:** A small orchestration framework that composes three AI agents — planner, coder, and reviewer — into a state graph workflow. The system accepts a user request, generates an implementation plan, writes code, and reviews the result.

**Key Features**

- **Planner:** Produces concise implementation plans and file-structure suggestions using an LLM. See [agents/planner.py](agents/planner.py).
- **Coder:** Implements the plan by creating files and running verification commands. See [agents/coder.py](agents/coder.py).
- **Reviewer:** Inspects the generated project and provides approval feedback. See [agents/reviewer.py](agents/reviewer.py).
- **Workflow:** Orchestrates the agent nodes in a StateGraph. See [workflow.py](workflow.py).

**Requirements**

- Install Python dependencies listed in [requirements.txt](requirements.txt).

Installation

- Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Usage

- Run the main workflow to interact with the agents:

```bash
python3 workflow.py
```

The program prompts for a `User:` string, then runs the planner → coder → reviewer loop. The reviewer can cause the workflow to loop back to the coder or end execution when approved.

Project Structure

- **workflow.py:** Graph entrypoint that wires `planner`, `coder`, and `reviewer` nodes.
- **agents/**: Agent implementations and tools.
  - [agents/planner.py](agents/planner.py)
  - [agents/coder.py](agents/coder.py)
  - [agents/reviewer.py](agents/reviewer.py)
- **requirements.txt:** Python dependencies for LLM and orchestration libraries.

Development Notes

- The agents use `langchain`, `langgraph`, and `langchain-ollama` integrations (see [requirements.txt](requirements.txt)).
- `planner` writes plans and can persist requirement files via `write_requirements`.
- `coder` uses tools to write files and run bash commands to verify structure.
- `reviewer` uses file-listing and file-reading tools to approve or request changes.

Contributing

- Open an issue or submit a PR with clear description and tests where applicable.

License

- Add a license file if you wish to open-source this project.

Notes

- This README is a brief overview. For more detailed developer instructions, add a CONTRIBUTING.md and expand the agent prompts and system configurations.
