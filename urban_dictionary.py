import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
import re
from html import unescape
class urban_dictionary:
    def __init__(self) -> None:
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.7',
            'origin': 'https://www.urbandictionary.com',
            'priority': 'u=1, i',
            'referer': 'https://www.urbandictionary.com/',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Brave";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        }
        self.autocompelete_url = "https://api.urbandictionary.com/v0/autocomplete-extra"
        self.search_url = "https://www.urbandictionary.com/search.php"
        self.proxy = None
        self.title_pattern = r"<meta content=\"Urban Dictionary: ([\w ]*?)\" property=\"og:title\" /><meta content=\"@urbandictionary\""
        self.description_pattern = r"property=\"fb:app_id\" /><meta content=\"(.*?)\" name=\"Description\""
    def _make_connector(self, proxy: str = None):
        if proxy:
            self.proxy = proxy if proxy.startswith('http') else None
        return ProxyConnector.from_url(proxy) if proxy and proxy.startswith('socks') else aiohttp.TCPConnector()
    async def _autocomplete(self, query: str):
        params = {
            "term": query
        }
        async with self.session.get(self.autocompelete_url, params=params, headers=self.headers, proxy=self.proxy) as r:
            response = await r.json()
        return response['results']
    async def autocomplete(self, query: str, proxy: str = None):
        if hasattr(self, "session") and not self.session.closed:
            return await self._autocomplete(query)
        else:
            async with aiohttp.ClientSession(connector=self._make_connector(proxy)) as session:
                self.session = session
                return await self._autocomplete(query)
    async def _search(self, query: str):
        data = aiohttp.FormData()
        data.add_field("term", query)
        async with self.session.post(self.search_url, headers=self.headers, data=data, proxy=self.proxy) as r:
            response = await r.text()
        info = {}
        if title := re.search(self.title_pattern, response):
            info['title'] = unescape(title.group(1))
        else:
            raise ValueError("couldnt find the term")
        if definition := re.search(self.description_pattern, response):
            info['definition'] = unescape(definition.group(1))
        else:
            raise ValueError("couldnt find the term")
        return info
    async def search(self, query: str, proxy: str = None):
        if hasattr(self, "session") and not self.session.closed:
            return await self._search(query)
        else:
            async with aiohttp.ClientSession(connector=self._make_connector(proxy)) as session:
                self.session = session
                return await self._search(query)
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("term", type=str, help="term to search up")
    parser.add_argument("--proxy", type=str, help="proxy to use")
    args = parser.parse_args()
    urban = urban_dictionary()
    try:
        print(asyncio.run(urban.search(args.term, args.proxy)))
    except ValueError:
        print("Couldnt find that term. Perhaps you meant:")
        autocompl = asyncio.run(urban.autocomplete(args.term, args.proxy))
        print("\n".join(map(lambda x: x.get("term"), autocompl)))