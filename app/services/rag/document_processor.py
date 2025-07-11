import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain.document_loaders import (
    PyPDFLoader,
    TextLoader,
    DirectoryLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings
from app.core.errors import DocumentProcessingError

logger = logging.getLogger(__name__)


async def load_documents(directory_path: str) -> List[Dict[str, Any]]:
    try:
        directory = Path(directory_path)
        
        if not directory.exists():
            raise DocumentProcessingError(f"Directory does not exist: {directory_path}")
        
        logger.info(f"Loading documents from {directory_path}")
        
        pdf_loader = DirectoryLoader(
            directory_path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
        )
        
        text_loader = DirectoryLoader(
            directory_path,
            glob="**/*.txt",
            loader_cls=TextLoader,
        )
        
        pdf_docs = pdf_loader.load()
        text_docs = text_loader.load()
        
        all_docs = pdf_docs + text_docs
        
        logger.info(f"Loaded {len(all_docs)} documents")
        
        return all_docs
    except Exception as e:
        logger.exception(f"Error loading documents from {directory_path}")
        raise DocumentProcessingError(f"Error loading documents: {str(e)}")


async def split_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    try:
        logger.info(f"Splitting {len(documents)} documents into chunks")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
        
        chunks = text_splitter.split_documents(documents)
        
        logger.info(f"Split documents into {len(chunks)} chunks")
        
        return chunks
    except Exception as e:
        logger.exception("Error splitting documents")
        raise DocumentProcessingError(f"Error splitting documents: {str(e)}")


async def process_documents(directory_path: str) -> List[Dict[str, Any]]:
    try:
        documents = await load_documents(directory_path)
        
        chunks = await split_documents(documents)
        
        return chunks
    except Exception as e:
        logger.exception(f"Error processing documents from {directory_path}")
        raise DocumentProcessingError(f"Error processing documents: {str(e)}")