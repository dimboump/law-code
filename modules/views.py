import json
import re

import streamlit as st
from openai import OpenAI
from openai.types.responses.response_text_config_param import ResponseTextConfigParam

from config import ENV, MQM_PROMPTS
from modules.models import GPT

# from modules.mqm_oai import MQMAnnotation, get_openai_schema
from modules.mqm import MQMAnnotation, get_openai_schema

MQM_RESPONSE_SCHEMA = get_openai_schema(MQMAnnotation)


class ViewsManager:
    def __init__(self) -> None:
        self.system_prompt = "You are a helpful assistant."

    def get_main_view(self) -> None:
        self.get_sidebar()
        self.get_conversation_section()

    def get_system_prompt_area(self, with_structured_output: bool = False):
        if with_structured_output:
            scenario = st.radio("Σενάριο MQM:", options=["S-T", "R-T", "S-R-T"], key="scenario")

            system_prompt = MQM_PROMPTS[scenario].strip()
        else:
            system_prompt = self.system_prompt
        self.system_prompt = st.text_area("System prompt:", value=system_prompt)

        if "{" and "}" in self.system_prompt:
            with st.expander("Μεταβλητές στο system prompt", expanded=True):
                self.system_prompt = self.get_prompt_with_placeholders()

    def get_sidebar(self) -> None:
        with st.sidebar:
            if ENV in ("DEV", "UAT"):
                from config import OPENAI_API_KEY, OPENAI_MODEL

                openai_api_key = OPENAI_API_KEY
                openai_model = GPT[OPENAI_MODEL]
            else:
                openai_api_key = st.text_input("Κλειδί για το API της OpenAI:")
                openai_model = st.selectbox("Μοντέλο GPT:", options=list(GPT))

            st.toggle("Απάντηση για αξιολόγηση με MQM (σε JSON)", key="structured_output")

            self.get_system_prompt_area(
                with_structured_output=st.session_state["structured_output"]
            )

            temperature = st.number_input(
                "Temperature (μεταξύ 0 και 1)",
                value=0.1,
                min_value=float(0),
                max_value=float(1),
                step=0.1,
            )

            st.session_state["openai_model"] = openai_model or None
            st.session_state["openai_key"] = openai_api_key or None
            st.session_state["system_prompt"] = self.system_prompt
            st.session_state["temperature"] = temperature or 0

            system_tokens = st.session_state.conversation_handler.count_tokens(
                text=self.system_prompt, model=openai_model, role="system"
            )

            user_tokens = st.session_state.conversation_handler.user_tokens
            input_tokens = st.session_state.conversation_handler.input_tokens
            output_tokens = st.session_state.conversation_handler.output_tokens

            st.divider()

            input_col, output_col = st.columns(2)

            with input_col:
                input_cost = st.session_state.conversation_handler.calculate_cost(
                    input_tokens, model=openai_model, type="input"
                )
                st.write("## Input")
                st.write(
                    f"### {input_tokens} (${input_cost:.04f})  \n"
                    f"({system_tokens} συστήματος +  \n "
                    f"{user_tokens} μηνύματος)"
                )

            with output_col:
                output_cost = st.session_state.conversation_handler.calculate_cost(
                    output_tokens, model=openai_model, type="output"
                )
                st.write("## Output")
                if output_cost < 0.001:
                    output_cost_str = "0"
                else:
                    output_cost_str = f"{output_cost:.04f}"
                st.write(f"### {output_tokens} (${output_cost_str})")

            if ENV == "DEV":
                st.divider()
                st.write(st.session_state.to_dict())

    def get_conversation_section(self) -> None:
        openai_model = st.session_state["openai_model"]
        openai_api_key = st.session_state["openai_key"]

        with st.expander(
            "Τελικό system prompt", expanded=st.session_state.get("show_final_prompt", False)
        ):
            st.write(self.system_prompt)

        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

        placeholder_text = "Γράψε μου μήνυμα"
        if st.session_state["structured_output"]:
            placeholder_text += " για απάντηση με JSON"

        if prompt := st.chat_input(placeholder=placeholder_text):
            if not any([openai_api_key, openai_model]):
                st.info("Επίλεξε μοντέλο GPT και βάλε το κλειδί για το API.")
                st.stop()

            client = OpenAI(api_key=openai_api_key)

            st.session_state.conversation_handler.add_message({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            _ = st.session_state.conversation_handler.count_tokens(
                text=prompt, model=openai_model, role="user"
            )

            if st.session_state["structured_output"]:
                response_format: ResponseTextConfigParam = {
                    "format": {
                        "type": "json_schema",
                        "name": "mqm_annotation",
                        "strict": True,
                        "schema": MQM_RESPONSE_SCHEMA,
                    }
                }
            else:
                response_format = {"format": {"type": "text"}}

            response = client.responses.create(
                model=openai_model.value.api_name,
                instructions=st.session_state.system_prompt,
                input=st.session_state.conversation_handler.get_history(),
                temperature=st.session_state.temperature,
                text=response_format,  # type: ignore
            )

            if response.usage:
                print(f"Sent {response.usage.input_tokens} tokens")
                st.session_state.conversation_handler.output_tokens = response.usage.output_tokens
                print(f"Received {response.usage.output_tokens} tokens")

            msg = response.output_text
            st.session_state.conversation_handler.add_message({"role": "assistant", "content": msg})

            if st.session_state["structured_output"]:
                if isinstance(msg, str):
                    msg_dict = json.loads(msg)
                else:
                    msg_dict = msg
                st.chat_message("assistant").json(msg_dict)
            else:
                st.chat_message("assistant").write(msg)

            # TODO: Add helper buttons ("Clear convo", "Retry", "Export scenario")

    def get_prompt_with_placeholders(self) -> str:
        placeholders = re.findall(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", self.system_prompt)

        # Remove duplicates while preserving order
        seen = set()
        unique_placeholders = []
        for p in placeholders:
            if p not in seen:
                seen.add(p)
                unique_placeholders.append(p)

        if unique_placeholders:
            if "prompt_placeholders" not in st.session_state:
                st.session_state.prompt_placeholders = {}

            # Create a text input for each unique placeholder
            for placeholder in unique_placeholders:
                if placeholder not in st.session_state.prompt_placeholders:
                    st.session_state.prompt_placeholders[placeholder] = ""

                st.session_state.prompt_placeholders[placeholder] = st.text_input(
                    f"`{placeholder}`:",
                    value=st.session_state.prompt_placeholders[placeholder],
                    key=f"input_{placeholder}",
                )
                if "lang" in placeholder:
                    st.session_state.prompt_placeholders[placeholder] = (
                        st.session_state.prompt_placeholders[placeholder].upper()
                    )

            for placeholder in list(st.session_state.prompt_placeholders):
                if placeholder not in unique_placeholders:
                    del st.session_state.prompt_placeholders[placeholder]

            empty_placeholders = list(st.session_state.prompt_placeholders.values()).count("")
            if not empty_placeholders:
                st.session_state["show_final_prompt"] = True
                return self.system_prompt.format(**st.session_state.prompt_placeholders)
            else:
                middle = "μεταβλητές δεν έχουν" if empty_placeholders > 1 else "μεταβλητή δεν έχει"
                st.warning(f"{empty_placeholders} {middle} τιμή")
        return self.system_prompt
