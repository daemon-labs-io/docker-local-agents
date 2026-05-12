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
docker run --rm -v $(pwd)/workshop/data/models:/data/models curlimages/curl -L -o /data/models/qwen2.5-1.5b-instruct-Q4_K_M.gguf "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf?download=true"
```

```shell
docker run --rm -v $(pwd)/workshop/data/models:/data/models curlimages/curl -L -o /data/models/nomic-embed-text-v1.5.Q4_K_M.gguf "https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/resolve/main/nomic-embed-text-v1.5.Q4_K_M.gguf?download=true"
```

> [!IMPORTANT]  
> Once you've finished, [continue with the workshop](../README.md).
