import chromadb
from rag.embedder import get_embedding
client = chromadb.PersistentClient(
    path='./chroma_db'
)

collection = client.get_or_create_collection(
    name="novacart_conversation_memory"
)

def store_message_embedding(message_id: str, conversation_id:str, role:str, message_text:str) -> None:

    embedding = get_embedding(message_text)

    collection.add(
        ids=[message_id],
        embeddings=[embedding],
        documents=[message_text],
        metadatas=[{
            "conversation_id": conversation_id,
            "role": role
        }]
    )

def retrieve_historical_messages(conversation_id:str, query:str, top_k:int = 3) -> list[dict]:

    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={
            "conversation_id":conversation_id
        },
        include=["documents","metadatas","distances"]
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    memories = []

    for index, document in enumerate(documents):
        metadata = metadatas[index]
        distance = distances[index]

        memories.append({
            "role": metadata.get("role"),
            "message_text": document,
            "distance": distance
        })

    return memories