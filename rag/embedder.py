from langchain_ollama import OllamaEmbeddings

embedding_model = OllamaEmbeddings(model='nomic-embed-text')

def get_embedding(text:str) -> list[float]:
    return embedding_model.embed_query(text)

def get_embeddings(texts: list[str]) -> list[list[float]]:
    return embedding_model.embed_documents(texts)