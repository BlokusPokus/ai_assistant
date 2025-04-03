"""
Wikipedia tool implementation.
"""
from .base import Tool
from typing import Optional, Dict, Any
import requests


class WikipediaTool:
    def __init__(self):
        # Initialize any necessary configurations or tokens here
        self.api_url = "https://en.wikipedia.org/w/api.php"

        # Create individual tools
        self.search_tool = Tool(
            name="search_wikipedia",
            func=self.search_wikipedia,
            description="Search Wikipedia for a given query",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query for Wikipedia"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of search results to return",
                    "optional": True
                }
            }
        )

        self.summary_tool = Tool(
            name="get_wikipedia_summary",
            func=self.get_wikipedia_summary,
            description="Get a summary of a Wikipedia page",
            parameters={
                "title": {
                    "type": "string",
                    "description": "Title of the Wikipedia page"
                }
            }
        )

    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter([self.search_tool, self.summary_tool])

    def search_wikipedia(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search Wikipedia for a given query"""
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "format": "json"
        }
        response = requests.get(self.api_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to search Wikipedia: {response.text}"}

    def get_wikipedia_summary(self, title: str) -> Dict[str, Any]:
        """Get a summary of a Wikipedia page"""
        params = {
            "action": "query",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": title,
            "format": "json"
        }
        response = requests.get(self.api_url, params=params)
        if response.status_code == 200:
            pages = response.json().get("query", {}).get("pages", {})
            page = next(iter(pages.values()), {})
            # Check if the page has an extract
            summary = page.get("extract", "No summary available")
            if not summary:
                summary = "No summary available"
            return {
                "title": page.get("title", "Unknown"),
                "summary": summary
            }
        else:
            return {"error": f"Failed to get Wikipedia summary: {response.text}"}

    def get_page_categories(self, title: str) -> Dict[str, Any]:
        """Get categories of a Wikipedia page"""
        params = {
            "action": "query",
            "prop": "categories",
            "titles": title,
            "format": "json"
        }
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            pages = response.json().get("query", {}).get("pages", {})
            page = next(iter(pages.values()), {})
            categories = [cat['title'] for cat in page.get("categories", [])]
            return {
                "title": page.get("title", "Unknown"),
                "categories": categories
            }
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get page categories: {str(e)}"}

    def get_page_links(self, title: str) -> Dict[str, Any]:
        """Get links from a Wikipedia page"""
        params = {
            "action": "query",
            "prop": "links",
            "titles": title,
            "format": "json",
            "pllimit": "max"
        }
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            pages = response.json().get("query", {}).get("pages", {})
            page = next(iter(pages.values()), {})
            links = [link['title'] for link in page.get("links", [])]
            return {
                "title": page.get("title", "Unknown"),
                "links": links
            }
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get page links: {str(e)}"}

    def get_page_images(self, title: str) -> Dict[str, Any]:
        """Get images from a Wikipedia page"""
        params = {
            "action": "query",
            "prop": "images",
            "titles": title,
            "format": "json",
            "imlimit": "max"
        }
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            pages = response.json().get("query", {}).get("pages", {})
            page = next(iter(pages.values()), {})
            images = [img['title'] for img in page.get("images", [])]
            return {
                "title": page.get("title", "Unknown"),
                "images": images
            }
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get page images: {str(e)}"}

    def get_full_page_content(self, title: str) -> Dict[str, Any]:
        """Get full content of a Wikipedia page"""
        params = {
            "action": "query",
            "prop": "extracts",
            "titles": title,
            "format": "json",
            "explaintext": True
        }
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            pages = response.json().get("query", {}).get("pages", {})
            page = next(iter(pages.values()), {})
            content = page.get("extract", "No content available")
            return {
                "title": page.get("title", "Unknown"),
                "content": content
            }
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get full page content: {str(e)}"}

    def set_language(self, language: str):
        """Set the language for Wikipedia API requests"""
        self.api_url = f"https://{language}.wikipedia.org/w/api.php"


def test_wikipedia_tool():
    # Instantiate the WikipediaTool
    wiki_tool = WikipediaTool()

    # Test the search_wikipedia method
    search_results = wiki_tool.search_wikipedia(
        "Bilderberg meetings", limit=3)
    print("Search Results:")
    print(search_results)

    # Test the get_wikipedia_summary method
    summary = wiki_tool.get_wikipedia_summary("Bilderberg meetings")
    print("\nWikipedia Summary:")
    print(summary)


if __name__ == "__main__":
    test_wikipedia_tool()
