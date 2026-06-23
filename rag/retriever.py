from rag.vector_store import similarity_search


def retrieve_relevant_chunks(query: str, top_k: int = 3) -> list[dict]:
    results = similarity_search(query, top_k)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    retrieved_chunks = []

    for document, metadata, distance in zip(documents, metadatas, distances):
        retrieved_chunks.append({
            "content": document,
            "source_file": metadata.get("source_file"),
            "distance": distance
        })

    return retrieved_chunks