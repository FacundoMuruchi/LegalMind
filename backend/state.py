from langgraph.graph import MessagesState


class ChatInputState(MessagesState):
    pass


class ChatOutputState(MessagesState):
    pass


class LegalMindState(ChatInputState):
    document_text: str
