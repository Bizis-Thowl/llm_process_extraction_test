# Testing LLMs on their capability to extract process information

## Arize Phoenix

To work, this Repository requires a running [Arize Phoenix](https://phoenix.arize.com/) instance.

To start a local docker instance of Arize Phoenix on your PC, use the following command:

```shell
C:\> docker run --name arize-phoenix -p 6006:6006 -p 4317:4317 -i -t arizephoenix/phoenix:latest
C:\>
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

*Models already tested:*
- *Qwen3-30B-A3B-Instruct*
- *llama3.2:latest* 
- *granite4*
