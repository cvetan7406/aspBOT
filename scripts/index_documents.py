import asyncio
import logging
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rag.vector_store import index_documents
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    argument_parser = argparse.ArgumentParser(description="Index documents for ASP Bot")
    argument_parser.add_argument(
        "--directory",
        type=str,
        default=os.path.join("data", "documents"),
        help="Directory containing documents to index",
    )
    parsed_args = argument_parser.parse_args()
    
    try:
        documents_path = parsed_args.directory
        logger.info(f"Starting document indexing process from {documents_path}")
        await index_documents(documents_path)
        logger.info("Document indexing completed successfully")
    except Exception as error:
        logger.exception(f"Document indexing failed: {str(error)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())