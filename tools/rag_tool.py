from rag.retriever import retrieve_relevant_chunks


def rag_tool(state: dict) -> dict:
    question = state.get("rag_question", state["question"])
    print("RAG tool is invoked")

    try:
        retrieved_chunks = retrieve_relevant_chunks(question, top_k=3)

        return {
            "rag_result": {
                "success": True,
                "tool": "rag",
                "retrieved_chunks": retrieved_chunks,
                "error": None
            }
        }

    except Exception as error:
        return {
            "rag_result": {
                "success": False,
                "tool": "rag",
                "retrieved_chunks": [],
                "error": str(error)
            },
            "error": str(error)
        }