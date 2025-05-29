from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import CohereEmbeddings
import pandas as pd
from google import genai
from google.genai import types
from chromadb import Documents, EmbeddingFunction, Embeddings
from google.api_core import retry
import chromadb
import os

class GeminiEmbeddingFunction(EmbeddingFunction):
    # Specify whether to generate embeddings for documents, or queries
    document_mode = True
    client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

    def is_retriable(exception):
        # Customize this logic as needed for your use case
        return True

    @retry.Retry(predicate=is_retriable)
    def __call__(self, input: Documents) -> Embeddings:
        if self.document_mode:
            embedding_task = "retrieval_document"
        else:
            embedding_task = "retrieval_query"

        response = self.client.models.embed_content(
            model="models/text-embedding-004",
            contents=input,
            config=types.EmbedContentConfig(
                task_type=embedding_task,
            ),
        )
        return [e.values for e in response.embeddings]
def create_vector_db(food_data, symptom_data):
    food_docs = food_data.to_string(index=False)
    symptom_docs = symptom_data.to_string(index=False)
    documents = [food_docs, symptom_docs]
    DB_NAME = "googlecardb"
    embed_fn = GeminiEmbeddingFunction()
    embed_fn.document_mode = True

    chroma_client = chromadb.Client()
    db = chroma_client.get_or_create_collection(name=DB_NAME, embedding_function=embed_fn)
    db.add(documents=documents, ids=[str(i) for i in range(len(documents))])
    return db, embed_fn.client, embed_fn