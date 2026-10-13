# tree-nation-connector

Set of tools to interact with Tree-Nation.

## CLI usage

This repository provides a small Python CLI to call endpoints described in the Postman docs:

- https://documenter.getpostman.com/view/14383592/2sAYJ98xqX

Set your API key and call any endpoint path from the docs:

```bash
export TREE_NATION_API_KEY="your-api-key"
python tree_nation_connector.py /v1/projects --method GET --param page=1
```

POST example:

```bash
python tree_nation_connector.py /v1/projects --method POST --data '{"name":"my-project"}'
```
