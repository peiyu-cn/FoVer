# Private Directory

Store private files here. This directory is ignored by Git.

## API Configurations

For reproduction, you will need to create an `apikey.py`, with the provider API keys and base URLs.

Note that the API keys should be initialized as `SecretStr`, and the base URLs as `str`.
For example:
```python
from pydantic.types import SecretStr

anthropic_base_url = str("https://api.anthropic.com")
anthropic_base_url_nocache = str("https://api.anthropic.com")
anthropic_key = SecretStr("sk-ant-xxxxxx")

openai_base_url = str("https://api.openai.com/v1")
openai_key = SecretStr("sk-svcacct-xxxxxx")
```
