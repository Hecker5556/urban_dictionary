# Simple urban dictionary api interactor through aiohttp
* Includes autocomplete function
* Usage of proxy
* Fast and simple

# Installation
1. in terminal
```bash
git clone https://github.com/Hecker5556/urban_dictionary
```
2.
```bash
cd urban_dictionary
```
3.
```bash
pip install -r requirements.txt
```

# Usage
## In terminal
```bash
python urban_dictionary "goy slop" --proxy "socks4://127.0.0.1:9050"
```

## In python
```python
from urban_dictionary import urban_dictionary
import asyncio
# Not in async function
result = asyncio.run(urban_dictionary().search("goy slop"))
title = result.get("title")
description = result.get("description")

# In async function
async def main():
    import aiohttp
    urban = urban_dictionary()
    # Using your own session
    async with aiohttp.ClientSession() as session:
        urban.session = session

        results = await urban.search("goy slop")
        title = result.get("title")
        description = result.get("description")
        
    # Not using your own session
    results = await urban.autocomplete("huak tuah")

    print("\n".join(map(lambda x: x.get("term"), results)))
asyncio.run(main())
```