"""
Jesse Novel Factory - Main Orchestrator
Runs the complete production pipeline without n8n
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class NotionClient:
    def __init__(self):
        self.api_key = os.getenv("NOTION_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self.db_ids = {
            "characters": os.getenv("NOTION_CHARACTERS_DB"),
            "chapters": os.getenv("NOTION_CHAPTERS_DB"),
            "books": os.getenv("NOTION_BOOKS_DB"),
            "songs": os.getenv("NOTION_SONGS_DB")
        }
    
    def query_database(self, db_name, filter_obj=None):
        db_id = self.db_ids.get(db_name)
        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        body = {"filter": filter_obj} if filter_obj else {}
        resp = requests.post(url, headers=self.headers, json=body)
        return resp.json().get("results", [])


class ClaudeClient:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
    
    def generate(self, prompt, max_tokens=8000):
        url = "https://api.anthropic.com/v1/messages"
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        body = {"model": self.model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
        resp = requests.post(url, headers=headers, json=body)
        return resp.json().get("content", [{}])[0].get("text", "")


class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("GPT_MODEL", "gpt-4-turbo-preview")
    
    def generate(self, prompt, system_prompt=None, json_mode=False):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        body = {"model": self.model, "messages": messages}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        resp = requests.post(url, headers=headers, json=body)
        return resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")


class JesseFactory:
    def __init__(self):
        self.notion = NotionClient()
        self.claude = ClaudeClient()
        self.openai = OpenAIClient()
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./outputs"))
        self.logs_dir = Path(os.getenv("LOGS_DIR", "./logs"))
        self.output_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    def log(self, stage, data):
        timestamp = datetime.now().isoformat()
        log_file = self.logs_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps({"timestamp": timestamp, "stage": stage, "data": data}) + "\n")
        print(f"[{timestamp}] {stage}: {str(data)[:100]}...")
    
    def load_prompts(self):
        prompts_dir = Path(__file__).parent / "prompts"
        prompts = {}
        for f in prompts_dir.glob("*.md"):
            prompts[f.stem] = f.read_text()
        return prompts


class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("GPT_MODEL", "gpt-4-turbo-preview")
    
    def generate(self, prompt, system_prompt=None, json_mode=False):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        body = {"model": self.model, "messages": messages}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        resp = requests.post(url, headers=headers, json=body)
        return resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")


class JesseFactory:
    def __init__(self):
        self.notion = NotionClient()
        self.claude = ClaudeClient()
        self.openai = OpenAIClient()
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./outputs"))
        self.logs_dir = Path(os.getenv("LOGS_DIR", "./logs"))
        self.output_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    def log(self, stage, data):
        timestamp = datetime.now().isoformat()
        log_file = self.logs_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps({"timestamp": timestamp, "stage": stage, "data": data}) + "\n")
        print(f"[{timestamp}] {stage}: {str(data)[:100]}...")
    
    def load_prompts(self):
        prompts_dir = Path(__file__).parent / "prompts"
        prompts = {}
        for f in prompts_dir.glob("*.md"):
            prompts[f.stem] = f.read_text()
        return prompts


class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("GPT_MODEL", "gpt-4-turbo-preview")
    
    def generate(self, prompt, system_prompt=None, json_mode=False):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        body = {"model": self.model, "messages": messages}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        resp = requests.post(url, headers=headers, json=body)
        return resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")


class JesseFactory:
    def __init__(self):
        self.notion = NotionClient()
        self.claude = ClaudeClient()
        self.openai = OpenAIClient()
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./outputs"))
        self.logs_dir = Path(os.getenv("LOGS_DIR", "./logs"))
        self.output_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    def log(self, stage, data):
        timestamp = datetime.now().isoformat()
        log_file = self.logs_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps({"timestamp": timestamp, "stage": stage, "data": data}) + "\n")
        print(f"[{timestamp}] {stage}: {str(data)[:100]}...")
    
    def load_prompts(self):
        prompts_dir = Path(__file__).parent / "prompts"
        prompts = {}
        for f in prompts_dir.glob("*.md"):
            prompts[f.stem] = f.read_text()
        return prompts


class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("GPT_MODEL", "gpt-4-turbo-preview")
    
    def generate(self, prompt, system_prompt=None, json_mode=False):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        body = {"model": self.model, "messages": messages}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        resp = requests.post(url, headers=headers, json=body)
        return resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")


class JesseFactory:
    def __init__(self):
        self.notion = NotionClient()
        self.claude = ClaudeClient()
        self.openai = OpenAIClient()
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./outputs"))
        self.logs_dir = Path(os.getenv("LOGS_DIR", "./logs"))
        self.output_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    def log(self, stage, data):
        timestamp = datetime.now().isoformat()
        log_file = self.logs_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps({"timestamp": timestamp, "stage": stage, "data": data}) + "\n")
        print(f"[{timestamp}] {stage}: {str(data)[:100]}...")
    
    def load_prompts(self):
        prompts_dir = Path(__file__).parent / "prompts"
        prompts = {}
        for f in prompts_dir.glob("*.md"):
            prompts[f.stem] = f.read_text()
        return prompts


class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("GPT_MODEL", "gpt-4-turbo-preview")
    
    def generate(self, prompt, system_prompt=None, json_mode=False):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        body = {"model": self.model, "messages": messages}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        resp = requests.post(url, headers=headers, json=body)
        return resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")


class JesseFactory:
    def __init__(self):
        self.notion = NotionClient()
        self.claude = ClaudeClient()
        self.openai = OpenAIClient()
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./outputs"))
        self.logs_dir = Path(os.getenv("LOGS_DIR", "./logs"))
        self.output_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    def log(self, stage, data):
        timestamp = datetime.now().isoformat()
        log_file = self.logs_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps({"timestamp": timestamp, "stage": stage, "data": data}) + "\n")
        print(f"[{timestamp}] {stage}: {str(data)[:100]}...")
    
    def load_prompts(self):
        prompts_dir = Path(__file__).parent / "prompts"
        prompts = {}
        for f in prompts_dir.glob("*.md"):
            prompts[f.stem] = f.read_text()
        return prompts


class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("GPT_MODEL", "gpt-4-turbo-preview")
    
    def generate(self, prompt, system_prompt=None, json_mode=False):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        body = {"model": self.model, "messages": messages}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        resp = requests.post(url, headers=headers, json=body)
        return resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")


class JesseFactory:
    def __init__(self):
        self.notion = NotionClient()
        self.claude = ClaudeClient()
        self.openai = OpenAIClient()
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./outputs"))
        self.logs_dir = Path(os.getenv("LOGS_DIR", "./logs"))
        self.output_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    def log(self, stage, data):
        timestamp = datetime.now().isoformat()
        log_file = self.logs_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps({"timestamp": timestamp, "stage": stage, "data": data}) + "\n")
        print(f"[{timestamp}] {stage}: {str(data)[:100]}...")
    
    def load_prompts(self):
        prompts_dir = Path(__file__).parent / "prompts"
        prompts = {}
        for f in prompts_dir.glob("*.md"):
            prompts[f.stem] = f.read_text()
        return prompts


class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("GPT_MODEL", "gpt-4-turbo-preview")
    
    def generate(self, prompt, system_prompt=None, json_mode=False):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        body = {"model": self.model, "messages": messages}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        resp = requests.post(url, headers=headers, json=body)
        return resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")


class JesseFactory:
    def __init__(self):
        self.notion = NotionClient()
        self.claude = ClaudeClient()
        self.openai = OpenAIClient()
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./outputs"))
        self.logs_dir = Path(os.getenv("LOGS_DIR", "./logs"))
        self.output_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    def log(self, stage, data):
        timestamp = datetime.now().isoformat()
        log_file = self.logs_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps({"timestamp": timestamp, "stage": stage, "data": data}) + "\n")
        print(f"[{timestamp}] {stage}: {str(data)[:100]}...")
    
    def load_prompts(self):
        prompts_dir = Path(__file__).parent / "prompts"
        prompts = {}
        for f in prompts_dir.glob("*.md"):
            prompts[f.stem] = f.read_text()
        return prompts

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)

    
    def run_showrunner(self, idea_brief, book_number=1):
        """Generate outline and first 2 chapters"""
        self.log("showrunner", {"status": "starting", "idea": idea_brief})
        canon = self.notion.query_database("canon")
        prompts = self.load_prompts()
        prompt = prompts.get("showrunner", "").replace("{{ideaBrief}}", idea_brief)
        result = self.claude.generate(prompt)
        self.log("showrunner", {"status": "complete", "length": len(result)})
        return result
    
    def run_continuity_qa(self, draft_text):
        """Check draft against canon"""
        self.log("continuity_qa", {"status": "starting"})
        system_prompt = "You are Continuity QA. Output JSON: {errors: [], risks: [], patches: []}"
        result = self.openai.generate(f"Check draft:\n{draft_text}", system_prompt, json_mode=True)
        self.log("continuity_qa", {"status": "complete"})
        try:
            return json.loads(result)
        except:
            return {"errors": [], "risks": [], "patches": []}
    
    def run_structural_editor(self, draft_text, patches):
        """Apply patches and improve pacing"""
        self.log("structural_editor", {"status": "starting", "patches": len(patches)})
        patches_text = "\n".join([f"- {p.get('location', '')}: {p.get('change', '')}" for p in patches])
        prompt = f"Apply patches:\n{patches_text}\n\nDraft:\n{draft_text}"
        result = self.claude.generate(prompt)
        return result
    
    def run_dialogue_punchup(self, draft_text):
        """Sharpen dialogue"""
        self.log("dialogue_punchup", {"status": "starting"})
        system_prompt = "Sharpen timing, improve back-and-forth, ensure Irish banter tone."
        result = self.openai.generate(f"Punch up dialogue:\n{draft_text}", system_prompt)
        return result
    
    def run_pipeline(self, idea_brief, book_number=1):
        """Run full pipeline"""
        print(f"\n{'='*60}\nJESSE NOVEL FACTORY - Book {book_number}\n{'='*60}\n")
        showrunner_output = self.run_showrunner(idea_brief, book_number)
        qa_result = self.run_continuity_qa(showrunner_output)
        edited = self.run_structural_editor(showrunner_output, qa_result.get("patches", []))
        final = self.run_dialogue_punchup(edited)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"book_{book_number}_{timestamp}.md"
        output_file.write_text(final)
        print(f"\nCOMPLETE: {output_file}\n")
        return final


if __name__ == "__main__":
    import sys
    factory = JesseFactory()
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jesse discovers a magical cake"
    factory.run_pipeline(idea)
