from typing import Any

from langchain_core.messages import AIMessage, SystemMessage

from agente.llm import get_llm
from agente.state import LegalMindState


SYSTEM_PROMPT = """Eres LegalMind, un agente de IA destinado a los abogados clientes de LegalTalent, una startup especializada en cumplimiento normativo.
Tu objetivo es ayudar a los abogados a revisar contratos mediante un análisis minucioso, práctico y con enfoque jurídico.
Céntrate en identificar riesgos, cláusulas que faltan, lenguaje ambiguo, cuestiones de cumplimiento normativo y puntos de negociación.
Sé preciso y útil, pero no pretendas sustituir el criterio profesional de un abogado."""

FORMAT_PROMPT = "La respuesta sera enviada por un chat de texto. optimiza tus respuestas para este formato, se conciso. no uses tablas"


def build_document_prompt(document_text: str) -> str:
    if not document_text.strip():
        return "El documento de Word esta vacio o no se pudo leer todavia."

    return f"""Este es el contenido completo del documento de Word abierto, que debe tratarse como el contrato bajo revision:

{document_text}"""


def llm_node(state: LegalMindState) -> dict[str, list[AIMessage]]:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        SystemMessage(content=FORMAT_PROMPT),
        SystemMessage(content=build_document_prompt(state.get("document_text", ""))),
        *state["messages"],
    ]
    result: Any = get_llm().invoke(messages)
    content = getattr(result, "content", result)
    return {"messages": [AIMessage(content=str(content))]}
