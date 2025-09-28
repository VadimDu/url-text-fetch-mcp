# URL webpage text fetcher with FastMCP for LLM/agents frontends such as LM-Studio

URL webpage text fetcher for FastMCP — fetch the main readable body text from a URL web page, with optional size limits.
Designed to be used with via MCP protocol with LLMs frontends such as [LM Studio](https://lmstudio.ai).
In addition, this tool can also fetch URL-links present on the fetched webpage.

## ✅ Features

- Extract the main text from URL webpages
- Optionally control the maximum number of returned characters (to reduce tokens usage for your LLM)
- Input validation with Pydantic scheme
- Works seamlessly with LM Studio via MCP protocol

## 🚀 Installation

Install directly from GitHub:

```
pip install git+https://github.com/VadimDu/url-text-fetch-mcp.git
```

Or install in development mode:

```
git clone https://github.com/VadimDu/url-text-fetch-mcp.git
cd pdf-tool
pip install -e .
```

## 🛠 Testing

To test the this mcp-tool before real usage by LLM/agent:
```
python -m url_text_fetcher.url_text_fetcher_mcp
```
or
```
fastmcp run url_text_fetcher/url_text_fetcher_mcp.py
```
If everything is working fine, you should see a message like this:
`[date time] INFO     Starting MCP server 'URL Text Fetcher' with transport 'stdio'`

## 🎉 Usage in LM Studio

Add the following to your `mcp.json` file:
```
{
	"url-text-fetcher": {
      "command": "python",
      "args": [
        "-m",
        "url_text_fetcher.url_text_fetcher_mcp"
      ]
    }
}
```
