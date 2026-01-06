import os

from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Τσο και Law"

try:
    usr = os.getlogin()
    ENV = "DEV"
except OSError:
    ENV = "PROD"

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."

MQM_BASE_PROMPT = """\
You are a professional translator evaluator. You are reviewing texts from Greek to German that are hosted on the Greek Civil Code. The translation should be accurate and fluent. There will be fidelity at syntax level, however, it is more important to preserve the meaning than to translate word-for-word. Be as accurate and picky as possible. Identify the errors in the following translation. Note that Major errors refer to actual translation or grammatical errors, and Minor errors refer to smaller imperfections, and purely subjective opinions about the translation.\n
"""

MQM_SOURCE_TEXT = """{src_lang} source: "{source}"\n\n"""
MQM_TARGET_TEXT = """{tgt_lang} translation: "{translation}"\n\n"""
MQM_REF_TEXT = """{tgt_lang} reference: "{reference}"\n\n"""

MQM_S_T_PROMPT = MQM_BASE_PROMPT + MQM_SOURCE_TEXT + MQM_TARGET_TEXT
MQM_R_T_PROMPT = MQM_BASE_PROMPT + MQM_REF_TEXT + MQM_TARGET_TEXT
MQM_S_R_T_PROMPT = MQM_BASE_PROMPT + MQM_SOURCE_TEXT + MQM_REF_TEXT + MQM_TARGET_TEXT

MQM_PROMPTS = {
    "S-T": MQM_S_T_PROMPT,
    "R-T": MQM_R_T_PROMPT,
    "S-R-T": MQM_S_R_T_PROMPT,
}
