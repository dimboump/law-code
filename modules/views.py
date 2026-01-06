import json

import regex
import streamlit as st
from openai import OpenAI
from openai.types.responses.response_text_config_param import ResponseTextConfigParam

from config import DEFAULT_SYSTEM_PROMPT, ENV, MQM_PROMPTS
from modules.models import GPT
from modules.mqm import MQMAnnotation, get_openai_schema

MQM_RESPONSE_SCHEMA = get_openai_schema(MQMAnnotation)


class ViewsManager:
    def __init__(self) -> None:
        self.system_prompt = DEFAULT_SYSTEM_PROMPT

    def get_main_view(self) -> None:
        with st.sidebar:
            self.get_sidebar()

        self.get_conversation_section()

    def get_sidebar(self) -> None:
        self.get_model_options()

        st.divider()

        self.info_box = st.empty()

        if st.button(
            f"Λήψη {'παραδείγματος' if st.session_state.structured_output else 'συνομιλίας'}",
            type="primary",
            use_container_width=True,
        ):
            if not len(st.session_state.get("messages", [])):
                st.error("Conversation is empty. Add messages to export it.")
            else:
                data, file_type, mime_type = (
                    st.session_state.conversation_handler.export_conversation()
                )

                if data:
                    st.download_button(
                        "Εξαγωγή συνομιλίας",
                        data=data,
                        file_name=f"conversation.{file_type}",
                        mime=f"text/{mime_type}",
                        on_click="ignore",
                        use_container_width=True,
                        icon=":material/download:",
                    )

        if ENV == "DEV":
            st.divider()
            st.write(dict(sorted(st.session_state.to_dict().items())))

    def get_cost_columns(self) -> None:
        input_col, output_col = st.columns(2)

        st.session_state.conversation_handler.count_tokens(
            text=self.system_prompt,
            model=st.session_state.model_options["openai_model"],
            role="system",
        )

        with input_col:
            input_cost = st.session_state.conversation_handler.calculate_cost(
                st.session_state.conversation_handler.input_tokens,
                model=st.session_state.model_options["openai_model"],
                type="input",
            )
            st.write("## Input")
            st.write(
                f"### {st.session_state.conversation_handler.input_tokens} (${input_cost:.04f})"
            )

            input_cost_breakdown = (
                f"({st.session_state.conversation_handler.system_tokens} συστήματος +  \n "
            )
            if st.session_state["structured_output"]:
                st.session_state.conversation_handler.count_tokens(
                    json.dumps(MQM_RESPONSE_SCHEMA, ensure_ascii=False, indent=2),
                    model=st.session_state.model_options["openai_model"],
                    role="json",
                )
                input_cost_breakdown += (
                    f"{st.session_state.conversation_handler.json_tokens} μοντέλου JSON + \n "
                )
            st.write(
                input_cost_breakdown
                + f"{st.session_state.conversation_handler.user_tokens} μηνύματος)"
            )

        with output_col:
            output_tokens = st.session_state.conversation_handler.output_tokens
            output_cost = st.session_state.conversation_handler.calculate_cost(
                output_tokens, model=st.session_state.model_options["openai_model"], type="output"
            )
            st.write("## Output")
            if output_cost < 0.001:
                output_cost_str = "0"
            else:
                output_cost_str = f"{output_cost:.04f}"
            st.write(f"### {output_tokens} (${output_cost_str})")

    def get_system_prompt_area(self):
        if st.session_state.get("structured_output", False):
            scenario = st.radio("Σενάριο MQM:", options=["S-T", "R-T", "S-R-T"], key="scenario")
            system_prompt = MQM_PROMPTS[scenario].strip()
        else:
            if st.session_state.get("prompt_placeholders", []):
                system_prompt = DEFAULT_SYSTEM_PROMPT
                st.session_state.conversation_manager.clear_prompt_placeholders()
            else:
                system_prompt = self.system_prompt

        self.system_prompt = st.text_area("System prompt:", value=system_prompt)

        if "{" in self.system_prompt and "}" in self.system_prompt:
            with st.expander("Μεταβλητές στο system prompt", expanded=True):
                self.system_prompt = self.get_prompt_with_placeholders()

    def get_model_options(self) -> None:
        if ENV in ("DEV", "UAT"):
            from config import OPENAI_API_KEY, OPENAI_MODEL

            openai_api_key = OPENAI_API_KEY
            openai_model = GPT[OPENAI_MODEL]
        else:
            openai_api_key = st.text_input("Κλειδί για το API της OpenAI:")
            openai_model = st.selectbox("Μοντέλο GPT:", options=list(GPT))

        st.toggle("Απάντηση για αξιολόγηση με MQM (σε JSON)", key="structured_output")

        self.get_system_prompt_area()

        temperature = st.number_input(
            "Temperature (μεταξύ 0 και 1)",
            value=0.1,
            min_value=float(0),
            max_value=float(1),
            step=0.1,
        )

        st.session_state["system_prompt"] = self.system_prompt
        st.session_state["model_options"] = {
            "openai_model": openai_model or None,
            "openai_key": openai_api_key or None,
            "temperature": temperature or 0,
        }
        st.session_state["tokens"] = {"input": 0, "output": 0}

    def get_conversation_section(self) -> None:
        openai_model = st.session_state.model_options["openai_model"]
        openai_api_key = st.session_state.model_options["openai_key"]

        with st.expander(
            "Τελικό system prompt", expanded=st.session_state.get("show_final_prompt", False)
        ):
            st.write(self.system_prompt)

        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        for msg in st.session_state["messages"]:
            if msg["role"] == "system":
                continue
            st.chat_message(msg["role"]).write(msg["content"])

        placeholder_text = "Γράψε μου μήνυμα"
        if st.session_state["structured_output"]:
            placeholder_text += " για απάντηση με JSON"

        if prompt := st.chat_input(placeholder=placeholder_text):
            if not any([openai_api_key, openai_model]):
                st.info("Επίλεξε μοντέλο GPT και βάλε το κλειδί για το API.")
                st.stop()

            client = OpenAI(api_key=openai_api_key)

            if not len(st.session_state["messages"]):
                st.session_state.conversation_handler.add_message(
                    {"role": "system", "content": self.system_prompt}
                )
                print("SYSTEM PROMPT ADDED:", f"{st.session_state.messages=}", sep="\n", end="\n\n")

            st.session_state.conversation_handler.add_message({"role": "user", "content": prompt})
            print("USER PROMPT ADDED:", f"{st.session_state.messages=}", sep="\n", end="\n\n")

            st.chat_message("user").write(prompt)

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
                input=st.session_state.messages,
                temperature=st.session_state.model_options["temperature"],
                text=response_format,  # type: ignore
            )

            if response.usage:
                st.session_state.tokens["input"] += response.usage.input_tokens
                st.session_state.tokens["output"] += response.usage.output_tokens
                self.info_box.info(
                    f"Sent **{response.usage.input_tokens}** and "
                    f"received **{response.usage.output_tokens}** tokens."
                )

            msg = response.output_text
            st.session_state.conversation_handler.add_message({"role": "assistant", "content": msg})
            print("LLM RESPONSE ADDED:", f"{st.session_state.messages=}", sep="\n", end="\n\n")

            if st.session_state["structured_output"]:
                if isinstance(msg, str):
                    msg_dict = json.loads(msg)
                else:
                    msg_dict = msg
                st.chat_message("assistant").json(msg_dict)
            else:
                st.chat_message("assistant").write(msg)

            st.session_state["response_done"] = True

            # TODO: Add helper buttons ("Clear convo", "Retry", "Export scenario")

    def get_prompt_with_placeholders(self) -> str:
        placeholders = regex.findall(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", self.system_prompt)

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
