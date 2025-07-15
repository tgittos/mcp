import subprocess
from dataclasses import dataclass
import dotenv
import os

from openai import OpenAI

dotenv.load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_command(command):
    """Executes a shell command and returns the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        return None

def read_file(file_path):
    """Reads a file and returns the content."""
    with open(file_path, "r") as f:
        return f.read()

def write_file(file_path, content):
    """Writes content to a file."""
    with open(file_path, "w") as f:
        f.write(content)

def llm_completion(prompt, model="gpt-4o-mini", temperature=0.0):
    """Completes a prompt using the LLM."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    return response.choices[0].message.content

def spwan_ralph_process(prompt):
    """Spawns a Ralph process."""
    python_path = sys.executable
    process = subprocess.Popen([python_path, "src/ralph/ralph.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.stdin.write(prompt.encode())
    process.stdin.close()
    return process


@dataclass
class RalphConfiguration:
    project_dir: str


class Ralph:
    def __init__(self, prompt: str):
        self.prompt = prompt
        self.is_complete = False

    def execute(self):
        """Executes the Ralph's task in a loop until completion."""
        while not self.is_complete:
            pass


if __name__ == "__main__":
    prompt = ""
    if len(sys.argv) < 2:
        if os.path.exists("AGENT.md"):
            with open("AGENT.md", "r") as f:
                prompt = f.read()
        else:
            print("No prompt provided and AGENT.md not found. Please provide a prompt or create an AGENT.md file.")
            exit(1)
    else:
        prompt = sys.argv[1]

    ralph = Ralph(prompt)
    ralph.execute()
