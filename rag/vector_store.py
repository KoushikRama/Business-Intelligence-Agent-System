import chromadb


chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="novacart_knowledge_base"
)

def store_chunks(chunks: list[dict]):

    ids = []
    documents = []
    metadatas = []

    for index, chunk in enumerate(chunks):

        ids.append(
            f"{chunk['source_file']}_{chunk['chunk_id']}"
        )

        documents.append(
            chunk["content"]
        )

        metadatas.append({
            "source_file": chunk["source_file"]
        })

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )


def similarity_search(query: str,top_k: int = 3):
    
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    return results