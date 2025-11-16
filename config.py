import os

from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "PROD")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

MQM_PROMPT = """
You are a professional translator evaluator. You are reviewing texts from Greek to German that are hosted on the Greek Civil Code. The translation should be accurate and fluent. There will be fidelity at syntax level, however, it is more important to preserve the meaning than to translate word-for-word. Be as accurate and picky as possible. Identify the errors in the following translation. Note that Major errors refer to actual translation or grammatical errors, and Minor errors refer to smaller imperfections, and purely subjective opinions about the translation.

{src_lang} source: "{source}"

{tgt_lang} translation: "{translation}"
""".strip()
