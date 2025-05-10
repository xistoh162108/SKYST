from llm import GeminiLLM

class LLMAutoTags:
    def __init__(self):
        self.llm = GeminiLLM()

    def generate_tags(self, text: str) -> list[str]:
        prompt = f"Generate tags for the following text: {text}"
        response = self.llm.generate_text(prompt)
        return response.split(",")

