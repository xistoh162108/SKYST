import os
import requests
import subprocess
from typing import List, Dict, Optional

class GoogleSearchAPI:
    """
    Google Custom Search JSON API client.
    Requires environment variables:
      - GOOGLE_SEARCH_API_KEY
      - GOOGLE_SEARCH_CX (Custom Search Engine ID)
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 cx: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.cx = cx or os.getenv("GOOGLE_SEARCH_CX")
        if not self.api_key or not self.cx:
            raise RuntimeError("GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_CX must be set")
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search(self,
               query: str,
               num: int = 10,
               start: int = 1,
               safe: str = "off",
               **kwargs) -> List[Dict]:
        """
        Perform a search with the given query.
        :param query: Search keywords or phrase.
        :param num: Number of results to return (1-10).
        :param start: The index of the first result (1-indexed).
        :param safe: Safe search setting ("off", "medium", "high").
        :param kwargs: Additional query parameters.
        :return: List of result items as dictionaries.
        """
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "num": num,
            "start": start,
            "safe": safe,
        }
        params.update(kwargs)
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])

    def get_total_results(self, query: str) -> int:
        """
        Return the estimated total number of search results for a query.
        """
        results = self.search(query, num=1)
        # "searchInformation": {"totalResults": "12345", ...}
        info = requests.get(self.base_url, params={
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "num": 1
        }).json().get("searchInformation", {})
        return int(info.get("totalResults", 0))

    def get_page_content(self, url: str) -> str:
        """
        Fetch the HTML content of the given URL.
        :param url: The URL to fetch.
        :return: The HTML content as a string.
        """
        headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/113.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def download_site(self, url: str, target_dir: str):
        """
        Download/mirror the site at the given URL using wget.
        :param url: The URL to mirror.
        :param target_dir: The directory to save the mirrored site.
        """
        os.makedirs(target_dir, exist_ok=True)
        cmd = [
            "wget",
            "--mirror",
            "--convert-links",
            "--adjust-extension",
            "--page-requisites",
            "--no-parent",
            url
        ]
        subprocess.run(cmd, check=True, cwd=target_dir)