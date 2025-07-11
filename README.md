# ASP Bot

Bulgarian-language AI assistant for the Agency for Social Assistance in Bulgaria (Агенция за социално подпомагане - АСП).

## Overview

ASP Bot is a voice-activated Bulgarian-language AI assistant designed to help citizens navigate services and information provided by the Agency for Social Assistance in Bulgaria. The assistant uses a Retrieval-Augmented Generation (RAG) architecture to provide accurate, document-backed responses.

Key features:
- Voice activation with the wake phrase "Zdravey ASP"
- Bulgarian language speech-to-text and text-to-speech
- Document-based responses using RAG
- API endpoints for integration with frontend applications

## Technical Architecture

The system is built with the following components:

### 1. FastAPI Backend
- Provides RESTful API endpoints for voice interaction
- Handles request validation and error handling
- Manages service dependencies and configuration

### 2. RAG System
- **Document Processing**: Loads and processes PDF and text documents
- **Vector Store**: Uses Chroma DB to store document embeddings
- **Retriever**: Performs semantic search to find relevant document chunks
- **Answer Generation**: Uses OpenAI's GPT models to generate responses based on retrieved documents

### 3. Speech Processing
- **Speech-to-Text (STT)**: Uses Azure Speech Services to convert Bulgarian speech to text
- **Text-to-Speech (TTS)**: Uses Azure Speech Services to convert text responses to natural-sounding Bulgarian speech

### 4. Wake Word Detection
- Uses Picovoice Porcupine to detect the wake phrase "Zdravey ASP"
- Configurable sensitivity and detection parameters

## Data Flow

1. User speaks the wake phrase "Zdravey ASP"
2. Wake word detector activates the system
3. User's question is captured and converted to text using STT
4. The text query is processed by the RAG system:
   - Relevant documents are retrieved from the vector store
   - An answer is generated based on the retrieved documents
5. The text answer is converted back to speech using TTS
6. The audio response is played back to the user

## Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (optional, for containerized deployment)
- API Keys:
  - OpenAI API key (for embeddings and LLM)
  - Azure Speech Services key (for STT and TTS)
  - Picovoice Porcupine access key (for wake word detection)
- Sufficient disk space for document storage and vector database

## Installation

### Local Development

1. Clone the repository:
   ```
   git clone https://github.com/your-username/asp-bot.git
   cd asp-bot
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file with your API keys and configuration.

### Docker Deployment

1. Clone the repository:
   ```
   git clone https://github.com/your-username/asp-bot.git
   cd asp-bot
   ```

2. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```

3. Edit the `.env` file with your API keys and configuration.

4. Build and start the Docker container:
   ```
   docker-compose up -d
   ```

### Production Deployment

For production deployment, consider:

1. Using a reverse proxy (Nginx, Traefik) for SSL termination and load balancing
2. Setting up monitoring and logging (Prometheus, Grafana, ELK stack)
3. Implementing proper authentication for API endpoints
4. Using a managed Kubernetes service for container orchestration

Example Nginx configuration:
```nginx
server {
    listen 80;
    server_name asp-bot.example.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Configuration

The application is configured through environment variables, which can be set in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| API_HOST | Host to bind the API server | 0.0.0.0 |
| API_PORT | Port for the API server | 8000 |
| DEBUG | Enable debug mode | False |
| ENVIRONMENT | Environment (development, production) | production |
| SECRET_KEY | Secret key for security | (required) |
| OPENAI_API_KEY | OpenAI API key | (required) |
| AZURE_SPEECH_KEY | Azure Speech Services key | (required) |
| AZURE_SPEECH_REGION | Azure Speech Services region | (required) |
| AZURE_SPEECH_VOICE_NAME | Voice name for TTS | bg-BG-KalinaNeural |
| PORCUPINE_ACCESS_KEY | Picovoice Porcupine access key | (required) |
| VECTOR_STORE_PATH | Path to store vector database | ./data/processed/vector_store |
| EMBEDDING_MODEL | OpenAI embedding model | text-embedding-3-small |
| LLM_MODEL | OpenAI LLM model | gpt-4-turbo |
| CHUNK_SIZE | Document chunk size | 1000 |
| CHUNK_OVERLAP | Document chunk overlap | 200 |
| RETRIEVAL_TOP_K | Number of documents to retrieve | 3 |
| RELEVANCE_THRESHOLD | Minimum relevance score | 0.7 |

## Usage

### Indexing Documents

Before using the RAG system, you need to index your documents:

1. Place your PDF and TXT files in the `data/documents` directory.

2. Run the indexing script:
   ```
   python scripts/index_documents.py
   ```

This process:
- Loads documents from the specified directory
- Splits them into chunks
- Creates embeddings using OpenAI's embedding model
- Stores the embeddings in the Chroma vector database

### Starting the API Server

1. Start the API server:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. The API will be available at `http://localhost:8000`.

3. API documentation is available at `http://localhost:8000/docs` (in development mode).

### Testing Wake Word Detection

You can test the wake word detection with:

```
python scripts/test_wake_word.py
```

This will record audio from your microphone and check if the wake phrase is detected.

## API Endpoints

### Voice Interaction

#### `POST /api/v1/wake-word`
Detect wake word in audio.

Request:
```json
{
  "audio_data": "base64_encoded_audio"
}
```

Response:
```json
{
  "detected": true,
  "confidence": 0.85
}
```

#### `POST /api/v1/transcribe`
Transcribe audio to text.

Request:
```json
{
  "audio_data": "base64_encoded_audio"
}
```

Response:
```json
{
  "text": "Как мога да кандидатствам за социално подпомагане?"
}
```

#### `POST /api/v1/rag`
Query the RAG system.

Request:
```json
{
  "query": "Как мога да кандидатствам за социално подпомагане?"
}
```

Response:
```json
{
  "answer": "За да кандидатствате за социално подпомагане, трябва да подадете заявление в дирекция „Социално подпомагане" по настоящ адрес...",
  "sources": [
    {
      "content": "...",
      "metadata": {
        "source": "document1.pdf",
        "page": 5
      },
      "score": 0.92
    }
  ]
}
```

#### `POST /api/v1/tts`
Convert text to speech.

Request:
```json
{
  "text": "За да кандидатствате за социално подпомагане, трябва да подадете заявление в дирекция „Социално подпомагане" по настоящ адрес..."
}
```

Response:
```json
{
  "audio_data": "base64_encoded_audio"
}
```

#### `POST /api/v1/interact`
Complete voice interaction flow.

Request:
```json
{
  "audio_data": "base64_encoded_audio"
}
```

Response:
```json
{
  "text_response": "За да кандидатствате за социално подпомагане, трябва да подадете заявление в дирекция „Социално подпомагане" по настоящ адрес...",
  "audio_response": "base64_encoded_audio",
  "sources": [
    {
      "content": "...",
      "metadata": {
        "source": "document1.pdf",
        "page": 5
      },
      "score": 0.92
    }
  ]
}
```

### Health Check

#### `GET /health`
Check the health of the application and its services.

Response:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "services": {
    "vector_store": true,
    "openai": true,
    "azure_speech": true
  }
}
```

## Development

### Project Structure

```
asp-bot/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   └── voice.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── errors.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   ├── rag/
│   │   │   ├── document_processor.py
│   │   │   ├── retriever.py
│   │   │   └── vector_store.py
│   │   ├── speech/
│   │   │   ├── stt.py
│   │   │   └── tts.py
│   │   └── wake_word/
│   │       └── detector.py
│   ├── config.py
│   └── main.py
├── data/
│   ├── documents/
│   └── processed/
├── scripts/
│   ├── index_documents.py
│   └── test_wake_word.py
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

### Adding New Features

To add new features:

1. Create appropriate route handlers in `app/api/routes/`
2. Implement service logic in `app/services/`
3. Update schemas in `app/models/schemas.py` if needed
4. Add tests for new functionality

### Extending Document Support

To support additional document types:

1. Add appropriate loaders in `app/services/rag/document_processor.py`
2. Update the `load_documents` function to handle the new document types

Example for adding DOCX support:
```python
from langchain.document_loaders import Docx2txtLoader

# Add DOCX loader
docx_loader = DirectoryLoader(
    directory_path,
    glob="**/*.docx",
    loader_cls=Docx2txtLoader,
)

# Load documents
docx_docs = docx_loader.load()

# Combine documents
all_docs = pdf_docs + text_docs + docx_docs
```

## Troubleshooting

### Common Issues

#### Vector Store Initialization Fails

If the vector store fails to initialize:

1. Check if the `OPENAI_API_KEY` is valid
2. Ensure the `VECTOR_STORE_PATH` directory is writable
3. Try deleting the vector store directory and re-indexing documents

#### Wake Word Detection Issues

If wake word detection is not working:

1. Verify your `PORCUPINE_ACCESS_KEY` is valid
2. Check microphone permissions
3. Adjust the sensitivity parameter in the wake word detector

#### Speech Recognition Problems

If speech recognition is not working correctly:

1. Verify your `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION` are correct
2. Check audio input quality
3. Test with the Azure Speech Studio to verify service functionality

### Logs

Application logs are stored in the standard output and can be viewed:

- In local development: In the terminal where the application is running
- In Docker: Using `docker-compose logs -f`

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

### Code Style

This project follows PEP 8 style guidelines. Please ensure your code is formatted accordingly.

## Security Considerations

- API keys should never be committed to the repository
- In production, use proper authentication for API endpoints
- Consider rate limiting to prevent abuse
- Regularly update dependencies to address security vulnerabilities

## Performance Optimization

For better performance:

- Use a production ASGI server like Uvicorn with Gunicorn
- Consider caching frequent queries
- Optimize document chunking parameters for your specific documents
- Use a more powerful embedding model for better retrieval accuracy

## License

[MIT License](LICENSE)

## Acknowledgements

- OpenAI for Whisper and GPT models
- Azure for Speech Services
- Picovoice for Porcupine wake word detection
- LangChain for RAG implementation