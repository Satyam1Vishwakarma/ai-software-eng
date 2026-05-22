from langchain.tools import tool
from langchain.agents import create_agent
from langchain_ollama import ChatOllama


# ==========================================
# LLM
# ==========================================

llm = ChatOllama(
    model="qwen3:4b-instruct",
    temperature=0
)


# ==========================================
# TOOL
# ==========================================

@tool
def write_code(path: str, content: str) -> str:
    """Write project code inside the workspace folder"""

    import os
    import traceback

    try:

        # Force all files into workspace/
        workspace_root = "workspace"

        # Clean dangerous paths
        path = path.strip().lstrip("/")

        # Final absolute project path
        full_path = os.path.join(workspace_root, path)

        # Create folders automatically
        folder = os.path.dirname(full_path)

        if folder:
            os.makedirs(folder, exist_ok=True)

        # Write file
        with open(full_path, "w") as f:
            f.write(content)

        return f"{full_path} created successfully."

    except Exception as e:

        traceback.print_exc()

        return f"ERROR WRITING FILE: {str(e)}"

@tool
def bash_command(command: str) -> str:
    """Execute a bash command inside workspace"""

    import subprocess
    import os

    workspace_root = "workspace"

    os.makedirs(workspace_root, exist_ok=True)

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        cwd=workspace_root
    )

    if result.returncode != 0:
        return f"Error: {result.stderr}"

    return result.stdout

# ==========================================
# AGENT
# ==========================================

coder_agent = create_agent(
    model=llm,
    tools=[write_code, bash_command],
    system_prompt="""
You are a senior software engineer responsible for implementing software projects.

Your responsibilities:

0. Do all work in ./workspace folder.
1. Read the implementation plan carefully.
2. Create ALL folders and files mentioned in the plan.
3. Use the write_code tool to write EVERY file.
4. Use correct file paths when creating nested folders and files.
5. Generate COMPLETE production-ready code.
6. Never write placeholder code.
7. Never write explanations instead of code.
8. Never wrap code in markdown.
9. If a file already exists, overwrite it with improved code.
10. Use the bash_command tool to:
   - verify file creation
   - inspect folders
   - check project structure
   - debug issues if needed

Workflow you MUST follow:

Step 1:
Analyze the implementation plan and identify:
- folders
- files
- dependencies
- architecture

Step 2:
Create the required folder structure.

Step 3:
Write ALL required files using write_code.

Step 4:
Use bash_command to verify:
- files exist
- folders exist
- structure is correct

Step 5:
Fix missing files or structural problems if found.

Step 6:
If review feedback exists:
- improve the implementation
- fix bugs
- refactor bad code
- rewrite broken architecture if necessary

Important rules:

- You are writing REAL source files.
- Do NOT generate markdown documentation unless requested.
- Do NOT output code directly in chat.
- ALWAYS use tools.
- Ensure imports between files are correct.
- Ensure the project can run successfully.
- Be autonomous and proactive.
"""
)


# ==========================================
# NODE
# ==========================================
def coder_node(state):

    response = coder_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"""
Implementation Plan:

{state["plan"]}

Previous Review Feedback:

{state.get("review", "No previous review feedback.")}

Your task:
- build the complete project
- create all required folders
- create all required files
- implement all functionality
- verify the structure using bash commands
- fix issues automatically if found
"""
            }
        ]
    })

    code_result = response["messages"][-1].content

    print("\n========== CODER ==========\n")
    print(code_result)

    return {
        "code_result": code_result
    }