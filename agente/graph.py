from functools import lru_cache

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from agente.nodos.llm import llm_node
from agente.nodos.load_document import load_document_node
from agente.state import ChatInputState, ChatOutputState, LegalMindState


@lru_cache(maxsize=1)
def get_chat_graph():
    graph_builder = StateGraph(
        LegalMindState,
        input_schema=ChatInputState,
        output_schema=ChatOutputState,
    )

    graph_builder.add_node("load_document", load_document_node)
    graph_builder.add_node("llm", llm_node)
    
    graph_builder.add_edge(START, "load_document")
    graph_builder.add_edge("load_document", "llm")
    graph_builder.add_edge("llm", END)

    return graph_builder.compile(checkpointer=InMemorySaver())
