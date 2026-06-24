def format_rag_context(rag_result: dict | None) -> str:
    if not rag_result:
        return ""

    retrieved_chunks = rag_result.get("retrieved_chunks", [])

    if not retrieved_chunks:
        return ""

    context = ""

    for index, chunk in enumerate(retrieved_chunks, start=1):
        source_file = chunk.get("source_file", "Unknown source")
        content = chunk.get("content", "")

        context += f"""
        Source {index}: {source_file}
        Content:
        {content}
        """

    return context