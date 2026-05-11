from langchain_core.runnables import RunnableConfig

from agente.state import LegalMindState


def load_document_node(state: LegalMindState, config: RunnableConfig) -> dict[str, str]:
    configurable = config.get("configurable", {})
    return {"document_text": str(configurable.get("document_text", ""))}
