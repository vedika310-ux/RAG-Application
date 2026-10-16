"""Prompt templates for RAG Question Answering."""

SYSTEM_PROMPT = """You are a document-based question answering assistant.

Use ONLY the retrieved context to answer the question.

If the retrieved context does not contain enough information, say:
'I could not find enough information in the uploaded documents to answer this question.'

Never invent facts.
Never pretend that information exists in the document when it does not.

Answer clearly and concisely."""


def format_qa_prompt(question: str, context: str) -> str:
    """
    Constructs the prompt combining context and question for the LLM.
    """
    return f"""Context from uploaded documents:
==================================================
{context}
==================================================

Question: {question}

Instructions:
Answer the question using ONLY the context provided above. If the context does not provide sufficient facts to answer the question accurately, reply exactly:
'I could not find enough information in the uploaded documents to answer this question.'"""
