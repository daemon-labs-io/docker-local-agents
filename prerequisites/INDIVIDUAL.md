# 🛑 Prerequisites - Individual

> [!IMPORTANT]  
> **At an in-person workshop?**  
> [Continue to workshop prerequisites](./WORKSHOP.md)

## Pull Docker images

Pull the images:

```shell
docker pull ollama/ollama:latest
```

<!--  -->

```shell
docker pull chromadb/chroma:latest
```

<!--  -->

```shell
docker pull python:3.11-slim
```

<!--  -->

```shell
docker pull curlimages/curl:latest
```

## Download models

```shell
docker run --rm -v $(pwd)/workshop/data/models:/data/models curlimages/curl -L -o /data/models/phi3-mini.gguf "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf?download=true"
```

```shell
docker run --rm -v $(pwd)/workshop/data/models:/data/models curlimages/curl -L -o /data/models/nomic-embed-text-v1.5.Q4_K_M.gguf "https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/resolve/main/nomic-embed-text-v1.5.Q4_K_M.gguf?download=true"
```

> [!IMPORTANT]  
> Once you've finished, [continue with the workshop](../README.md).
