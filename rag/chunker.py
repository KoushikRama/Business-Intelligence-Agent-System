from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_documents(documents:list[dict], chunk_size:int = 500, chunk_overlap:int = 50):

    splitter=RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap )

    chunks = []

    for document in documents:
        split_texts = splitter.split_text(document["content"])
        for index,split_text in enumerate(split_texts):
            chunks.append(
                {
                    "source_file":document["filename"],
                    "chunk_id":index,
                    "content":split_text
                }
            )
    
    return chunks


        