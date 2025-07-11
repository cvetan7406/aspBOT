import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

from app.config import settings
from app.core.errors import VectorStoreError
from app.services.rag.document_processor import process_documents

logger = logging.getLogger(__name__)

vector_store = None
embeddings = None


async def initialize_embeddings():
    global embeddings
    
    try:
        if embeddings is None:
            embeddings = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
            )
            logger.info("Embeddings model initialized successfully")
        
        return embeddings
    except Exception as e:
        logger.exception("Failed to initialize embeddings model")
        raise VectorStoreError(f"Failed to initialize embeddings model: {str(e)}")


async def initialize_vector_store():
    global vector_store, embeddings
    
    try:
        if embeddings is None:
            await initialize_embeddings()
        
        vector_store_path = Path(settings.VECTOR_STORE_PATH)
        
        if vector_store_path.exists():
            vector_store = Chroma(
                persist_directory=str(vector_store_path),
                embedding_function=embeddings,
            )
            logger.info(f"Loaded existing vector store from {settings.VECTOR_STORE_PATH}")
        else:
            vector_store_path.parent.mkdir(parents=True, exist_ok=True)
            
            vector_store = Chroma(
                persist_directory=str(vector_store_path),
                embedding_function=embeddings,
            )
            logger.info(f"Created new vector store at {settings.VECTOR_STORE_PATH}")
        
        return vector_store
    except Exception as e:
        logger.exception("Failed to initialize vector store")
        vector_store = None
        raise VectorStoreError(f"Failed to initialize vector store: {str(e)}")


async def get_vector_store():
    global vector_store
    
    if vector_store is None:
        await initialize_vector_store()
    
    return vector_store


async def index_documents(directory_path: str):
    try:
        logger.info(f"Indexing documents from {directory_path}")
        
        chunks = await process_documents(directory_path)
        
        if not chunks:
            logger.warning(f"No documents found in {directory_path}")
            return
        
        store = await get_vector_store()
        
        store.add_documents(chunks)
        
        store.persist()
        
        logger.info(f"Indexed {len(chunks)} document chunks")
    except Exception as e:
        logger.exception(f"Error indexing documents from {directory_path}")
        raise VectorStoreError(f"Error indexing documents: {str(e)}")


async def similarity_search(query: str, k: int = 3) -> List[Dict[str, Any]]:
    try:
        store = await get_vector_store()
        
        results = store.similarity_search_with_relevance_scores(query, k=k)
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score,
            })
        
        return formatted_results
    except Exception as e:
        logger.exception(f"Error performing similarity search for query: {query}")
        raise VectorStoreError(f"Error performing similarity search: {str(e)}")


async def check_vector_store() -> bool:
    try:
        await get_vector_store()
        return True
    except Exception:
        logger.exception("Vector store check failed")
        return False