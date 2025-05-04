import asyncio
import aiohttp

URL = "https://api.ipify.org?format=json"

# Your authenticated proxy
proxy_url = "http://pawanjadam:IPTEH05-XAEOCXU-6ASWE2Z-LWBAZQG-RW0P9NA-OLX2BOS-VZCRKZ5@private.residential.proxyrack.net:10000"

async def fetch_ip(session, index):
    try:
        async with session.get(URL, proxy=proxy_url, timeout=10) as response:
            data = await response.json()
            print(f"Request {index}: IP = {data['ip']}")
            return data['ip']
    except Exception as e:
        print(f"Request {index} failed: {e}")
        return None

async def main():
    connector = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_ip(session, i) for i in range(1, 101)]
        ips = await asyncio.gather(*tasks)
    print("\nUnique IPs collected:", set(filter(None, ips)))

# Run it
asyncio.run(main())

