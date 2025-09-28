#!/usr/bin/env python3
"""
Url webpage text fetcher for FastMCP — fetch the main readable body text from a URL web page, with optional size limits.
Designed to be used with via MCP protocol with LLMs frontends such as LM-Studio.
"""


from fastmcp import FastMCP  # ← newer import style that expects Pydantic style annotation
import requests
import sys
import time
from bs4 import BeautifulSoup, NavigableString, Tag
from typing import List, ClassVar
from pydantic import BaseModel, HttpUrl, Field, PositiveInt  # <-- for the Pydantic schema


class UrlArg(BaseModel):
    """
    Pydantic model to validate and type-hint input parameters for both tools.
    * "url" - required fully-qualified HTTP/HTTPS URL. Positional argument (...).
    * "max_chars" - optional hard cut-off in **characters** (default: 40000), ratio of 1:4 of tokens to chars. Optional argument.
    """

    MAX_CHARS: ClassVar[int] = 40000  # hard-coded chars limit, add explicit type annotation and tells Pydantic to ignore it (“this is not a field” )

    url: HttpUrl = Field(...,
        description="The address of the web page you want to fetch."
    )
    max_chars: PositiveInt = Field(
        default=MAX_CHARS,
        description=(
            "Maximum number of characters to return. If omitted the server "
            f"uses the hard-coded default {MAX_CHARS}."
        ),
    )


mcp = FastMCP("URL Text Fetcher")  # shown in LM Studio UI


def _clean_body(html: str) -> str:
    """
    Helper function: “extract main visible text” from HTML page
    Return a string that contains only the *readable* body content.
    Steps:
      1. Parse with BeautifulSoup.
      2. Drop <script>, <style>, <noscript>, <header>, <footer>, <nav>.
      3. Keep text from <p>, headings, list items and blockquotes - these are
         the parts that usually constitute the main article body.
      4. Collapse whitespace to a single space and strip leading/trailing blanks.
    """

    soup = BeautifulSoup(html, "html.parser")

    # Remove boiler‑plate tags that never contain the “main article”
    for element in soup.find_all(["script", "style", "noscript", "header", "footer", "nav"]):
        element.decompose()

    # Locate the <body> (fallback to whole document if missing).
    body = soup.body or soup

    # “all visible text/elements” that exists under <body> (but without duplication)
    cleaned = " ".join(body.stripped_strings)

    # Whitespace normalisation (collapse multiple spaces/tabs/newlines into a single space)
    return " ".join(cleaned.split())


@mcp.tool(description="Fetch the main readable body text from a URL web page, with optional size limits.")
def fetch_url_text(args: UrlArg) -> str:
    """
    1. Retrieve the textual content of a page (*args.url*).
    2. Strip out scripts, navigation, etc., and keep only the visible
       content (paragraphs, headings, list items, etc.).
    3. Apply a hard limit of "max_chars" (ratio of 1:4 of tokens to chars)
    """

    # Download the raw HTML
    resp = requests.get(str(args.url), timeout=10)
    resp.raise_for_status()
    html = resp.text

     # Keep only the main body text
    cleaned = _clean_body(html)

    # Apply size limits
    result = cleaned[:args.max_chars]

    return result


@mcp.tool(description="Return a list of every URL hyperlink (href) found on a page.")
def fetch_page_links(args: UrlArg) -> List[str]:
    """
    Crawl *args.url* and collect the value of each ``href`` attribute
    from `<a>` elements.  The returned list contains the raw strings as
    they appear in the HTML (relative URLs are **not** resolved).
    """

    resp = requests.get(str(args.url), timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    links: List[str] = [a["href"] for a in soup.find_all("a", href=True)]
    return links


def main() -> None:
    """
    Launch the MCP server that hosts the 2 MCP functions defined above. FastMCP will pick an available port automatically. 
    LM-Studio will launch this file via the command you configured in *mcp.json*.
    """
   
    try:
        # Write to stderr immediately so LM Studio knows we're alive
        print("URL-Text-Fetcher MCP server starting...", file=sys.stderr)

        # OPTIONAL: Add a tiny delay if you have heavy module imports
        # This gives LM Studio time to connect before your server is ready
        # Remove this in production if you don't need it.
        time.sleep(0.5)

        # Start the server — this will block and wait for MCP messages
        print("URL-Text-Fetcher MCP server ready to receive requests...", file=sys.stderr)
        mcp.run(transport="stdio")

    except Exception as e:
        print(f"URL-Text-Fetcher crashed: {type(e).__name__}: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
