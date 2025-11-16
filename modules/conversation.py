from modules.models import GPT, count_tokens

type Message = dict[str, str]


class ConversationHandler:
    def __init__(self) -> None:
        self.history: list[Message] = []
        self.system_tokens = 0
        self.user_tokens = 0
        self.input_tokens = self.system_tokens + self.user_tokens
        self.output_tokens = 0

    def add_message(self, message: Message) -> None:
        self.history.append(message)

    def get_system_prompt(self) -> Message:
        return self.history[0]

    def get_history(self) -> list[Message]:
        return self.history

    def count_tokens(self, text: str, model: GPT, role: str | None = None) -> int:
        n_tokens = count_tokens(text, model)

        if role == "system":
            self.system_tokens += n_tokens
        elif role == "user":
            self.user_tokens += n_tokens

        self.input_tokens += n_tokens

        return n_tokens

    def calculate_cost(self, n_tokens: int, model: GPT, type: str = "input") -> float:
        if type == "input":
            cost_per_million = model.value.input_tokens_cost
        else:
            cost_per_million = model.value.output_tokens_cost
        return n_tokens * (cost_per_million / 1_000_000)
