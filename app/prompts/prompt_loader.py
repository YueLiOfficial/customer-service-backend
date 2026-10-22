from pathlib import Path

def load_prompt(file_name: str) -> str:
    file_path = Path(__file__).parent / "prompt" / f"{file_name}.jinja2"
    return file_path.read_text(encoding="utf-8")

if __name__ == "__main__":
    text = load_prompt("knowledge_respond")
    print(text)