# 🛑 Prerequisites - Workshop

> [!IMPORTANT]  
> **Not at an in-person workshop or having issues?**  
> [Continue to individual prerequisites](./INDIVIDUAL.md)

## Pull Docker images from local mirror

Pull the images:

```shell
docker pull registry.labs.dae.mn/ollama:latest
```

<!--  -->

```shell
docker pull registry.labs.dae.mn/chroma:latest
```

<!--  -->

```shell
docker pull registry.labs.dae.mn/python:3.11-slim
```

<!--  -->

```shell
docker pull registry.labs.dae.mn/curl:latest
```

Retag to original names for use in docker-compose:

```shell
docker tag registry.labs.dae.mn/ollama:latest ollama/ollama:latest
docker tag registry.labs.dae.mn/chroma:latest chromadb/chroma:latest
docker tag registry.labs.dae.mn/python:3.11-slim python:3.11-slim
docker tag registry.labs.dae.mn/curl:latest curlimages/curl:latest
```

## Download models

```shell
docker run --rm -v $(pwd)/workshop/data/models:/data/models curlimages/curl -o /data/models/phi3-mini.gguf https://files.labs.dae.mn/phi3-mini.gguf
```

```shell
docker run --rm -v $(pwd)/workshop/data/models:/data/models curlimages/curl -o /data/models/nomic-embed-text-v1.5.Q4_K_M.gguf https://files.labs.dae.mn/nomic-embed-text-v1.5.Q4_K_M.gguf
```

> [!IMPORTANT]  
> Once you've finished, [continue with the workshop](../README.md).  
> If you're having issues, [try the individual prerequisites](./INDIVIDUAL.md).
