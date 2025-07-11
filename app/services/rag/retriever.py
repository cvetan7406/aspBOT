import logging
from typing import List, Dict, Any, Tuple, Optional
import openai

from app.config import settings
from app.core.errors import RAGError, NoRelevantDocumentsError
from app.services.rag.vector_store import similarity_search

logger = logging.getLogger(__name__)


async def query_rag_system(query: str) -> Tuple[str, List[Dict[str, Any]]]:
    try:
        results = await similarity_search(
            query=query,
            k=settings.RETRIEVAL_TOP_K,
        )
        
        if not results:
            logger.warning(f"No relevant documents found for query: {query}")
            raise NoRelevantDocumentsError()
        
        relevant_results = [
            result for result in results
            if result["score"] >= settings.RELEVANCE_THRESHOLD
        ]
        
        if not relevant_results:
            logger.warning(f"No documents above relevance threshold for query: {query}")
            raise NoRelevantDocumentsError()
        
        answer = await generate_answer(query, relevant_results)
        
        return answer, relevant_results
    except NoRelevantDocumentsError:
        raise
    except Exception as e:
        logger.exception(f"Error querying RAG system for query: {query}")
        raise RAGError(f"Error querying RAG system: {str(e)}")


async def generate_answer(query: str, documents: List[Dict[str, Any]]) -> str:
    try:
        context = "\n\n".join([doc["content"] for doc in documents])
        
        prompt = f"""
Ти си полезен асистент, който помага на хората в България да разберат услугите на Агенцията за социално подпомагане. Може да отговаряш само на базата на следната информация:

{context}

Въпрос: {query}

Отговори само на български, използвайки само информацията по-горе. Ако не можеш да отговориш, кажи:
"Моля, опитайте се да формулирате въпроса по-точно, за да мога да помогна."
"""
        
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "Ти си полезен асистент, който помага на хората в България да разберат услугите на Агенцията за социално подпомагане."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=1000,
        )
        
        answer = response.choices[0].message.content.strip()
        
        logger.info(f"Generated answer for query: {query[:50]}...")
        return answer
    except Exception as e:
        logger.exception(f"Error generating answer for query: {query}")
        raise RAGError(f"Error generating answer: {str(e)}")