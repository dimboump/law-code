import json
from io import BytesIO
from uuid import uuid4

import numpy as np
import pandas as pd
import streamlit as st

from modules.models import GPT

type Message = dict[str, str]


class ConversationHandler:
    def __init__(self) -> None:
        st.session_state.messages = []

    def add_message(self, message: Message) -> None:
        st.session_state.messages.append(message)

    def get_system_prompt(self) -> str:
        return st.session_state.messages[0]["content"]

    def get_history(self) -> list[Message]:
        return st.session_state.messages

    def clear_prompt_placeholders(self) -> None:
        st.session_state.prompt_placeholders = []

    def export_conversation(self) -> tuple[bytes, str, str]:
        if st.session_state.structured_output:
            print("Exporting Excel file...")
            print(f"{st.session_state.prompt_placeholders=}")
            df = self.get_conversation_table()
            data = self.to_excel(df)  # type: ignore
            file_type = "xlsx"
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            print("Exporting plain text file...")
            data = "\n\n".join(
                [msg["content"].strip() for msg in st.session_state.messages]
            ).encode("utf-8")
            file_type, mime_type = "txt", "text/plain"

        return data, file_type, mime_type

    def get_conversation_table(self):
        prompt_placeholders: dict[str, str] = st.session_state.get("prompt_placeholders", [])

        if prompt_placeholders is None:
            st.error("Provide prompt placeholders to export the conversation.")

        system_prompt = self.get_system_prompt()
        print(f"Got {system_prompt=}")

        scenario = "S-T"
        if "reference:" in system_prompt:
            scenario = (
                "S-R-T" if "source:" in system_prompt and "translation:" in system_prompt else "R-T"
            )
        print(f"Got {scenario=}")

        for msg in st.session_state.messages:
            if msg["role"] != "assistant":
                continue

            try:
                data = json.loads(msg["content"].strip())
            except json.JSONDecodeError:
                raise ValueError("There is something wrong with the history. Try again later.")

            test_id = uuid4().hex
            rows = []
            print('About to iterate over data["errors"]')
            for err in data["errors"]:
                row = {
                    "test_id": test_id,
                    "test_scenario": scenario,
                    "error_id": uuid4().hex,
                    "source_language": (
                        prompt_placeholders["src_lang"] if "S-" in scenario else np.nan
                    ),
                    "target_language": (
                        prompt_placeholders["tgt_lang"] if "-T" in scenario else np.nan
                    ),
                    "reference_language": (
                        prompt_placeholders["tgt_lang"] if "R-" in scenario else np.nan
                    ),
                    "source_text": (prompt_placeholders["source"] if "S-" in scenario else np.nan),
                    "target_text": (
                        prompt_placeholders["translation"] if "-T" in scenario else np.nan
                    ),
                    "reference_text": (
                        prompt_placeholders["reference"] if "R-" in scenario else np.nan
                    ),
                    "error_category": err["category"],
                    "severity": err["severity"],
                    "source_tokens": err["in_source"]["token"],
                    "source_tokens_index": err["in_source"]["token_index"],
                    "source_character_span": err["in_source"]["character_span"],
                    "target_tokens": err["in_target"]["token"],
                    "target_tokens_index": err["in_target"]["token_index"],
                    "target_character_span": err["in_target"]["character_span"],
                }
                rows.append(row)
                print(f"{rows=}")
            return pd.DataFrame(rows).reset_index(drop=True)

    def to_excel(self, df: pd.DataFrame) -> bytes:
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        df.to_excel(writer, index=False)

        worksheet = writer.sheets["Sheet1"]
        worksheet.freeze_panes(1, 0)

        # 2. Text wrap and width for "_text" columns
        text_wrap_format = writer.book.add_format({"text_wrap": True})
        for idx, col in enumerate(df.columns):
            if "_text" in col:
                worksheet.set_column(idx, idx, 69, text_wrap_format)
            else:
                # 4. Autofit for other columns
                max_len = max([len(str(x)) for x in df[col].astype(str)] + [len(col)])
                worksheet.set_column(idx, idx, max_len + 2)

        # 3. Bold values under "scenario" column
        if "test_scenario" in df.columns:
            scenario_col_idx = df.columns.get_loc("test_scenario")
            bold_format = writer.book.add_format({"bold": True})
            worksheet.set_column(scenario_col_idx, scenario_col_idx, None, bold_format)

        writer.close()
        return output.getvalue()

    def calculate_cost(self, n_tokens: int, model: GPT, type: str = "input") -> float:
        if type == "input":
            cost_per_million = model.value.input_tokens_cost
        else:
            cost_per_million = model.value.output_tokens_cost
        return n_tokens * (cost_per_million / 1_000_000)
