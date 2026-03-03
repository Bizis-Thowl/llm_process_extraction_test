# Testing LLMs on their capability to extract process information

## Arize Phoenix

To work, this Repository requires a running [Arize Phoenix](https://phoenix.arize.com/) instance.

To start a local docker instance of Arize Phoenix on your PC, use the following command:

``` 
docker run --name arize-phoenix -p 6006:6006 -p 4317:4317 -i -t arizephoenix/phoenix:latest 
```

> **Note:** The name "arize-phoenix" can be changed or ommited entirely

A full documentation for running Arize Phoenix under Docker can be found under [this link](https://arize.com/docs/phoenix/self-hosting/deployment-options/docker).

## The language model

Refer to the [llm-docker-setup-Repository](https://github.com/Bizis-Thowl/llm_docker_setup) to set up your own language model with [Ollama](https://ollama.com) or [vLLM](https://vllm.ai/). 

You can also use an API like the OpenAI-API to run this program but **make sure not to include internal or sensitive information** if you do so.

## Last steps

Before starting: 
- Make sure to install the [required packages](/requirements.txt).
- Create a .env-file with the data that is listed in the .env-example
- Create a folder with the local data you want to work with.

And finally: Run [llm-process-extraction.py](/llm-process-extraction.py) to start

## Testing GraphRAG

To work with the GraphRAG-library from Microsoft you have to first open a terminal in the ``/graphrag_test``-folder. To initialize the environment run ``graphrag init``. The script will ask for the ``<language-model>`` and the ``<embedding-model>`` that you are going to use. This will create a bunch of files that are necessary for running the graphrag repository. If you are using Ollama, make sure that in the ``settings.yaml`` you  replace the data for the completion model and the embedding model with the following lines:

```
completion_models:
  default_completion_model:
    model_provider: ollama
    model: <language-model>
    auth_method: api_key # or azure_managed_identity
    api_key: ${GRAPHRAG_API_KEY} # set this in the generated .env file, or remove if managed identity
    api_base: <api-address>
    retry:
      type: exponential_backoff

embedding_models:
  default_embedding_model:
    model_provider: ollama
    model: <embedding-model>
    auth_method: api_key
    api_key: ${GRAPHRAG_API_KEY}
    api_base: <api-address>
    retry:
      type: exponential_backoff
```

Make shure to replace the text in the ``<>``-brackets with your own data. The following table will help you with this:

| name | purpose |
|---|---|
| ``<language-model>`` | Model that is used for the completions and execution of the RAG |
| ``<embedding-model>`` | Model that is used for the embedding of input-data |
| ``<api-adress>`` | Address of the API you want to call |

After that you can start the indexing-process with ``graphrag index`` in the commandline. The following process could take a few minutes.

After the indexing has finished, you are able to query the results with ``graphrag query "<query>"``