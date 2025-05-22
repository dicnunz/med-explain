# Med-Explain

A small Streamlit application that summarizes medical PDFs with the help of an
Ollama language model. The container image includes Tesseract for OCR and the
`ollama` Python package so the app can interact with an Ollama server.

## Requirements

Docker and Docker Compose are required to build and run the project.

## Build and Run

The recommended way to start the application is with Docker Compose which runs
both the Ollama server and the Streamlit app:

```bash
# Build the images and start the containers
docker compose up --build
```

The Streamlit interface will be available at
[http://localhost:8501](http://localhost:8501) and Ollama listens on port
`11434` for API calls.

To stop the containers press `Ctrl+C` and then run:

```bash
docker compose down
```

### Building the app image manually

You can also build the Streamlit application image separately:

```bash
docker build -t med-explain .
```

Run it with:

```bash
docker run -p 8501:8501 med-explain
```


