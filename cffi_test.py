import asyncio
from curl_cffi.requests import AsyncSession

async def get_session():
    # Create a new async session with curl_cffi
    session = AsyncSession(
        impersonate="chrome110",  # Optional: mimic Chrome browser
        timeout=30,  # Default timeout in seconds
        # You can add more options like proxies here
    )
    return session

async def fetch_profile():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        # Add other headers as needed
    }
    
    session = await get_session()
    response = await session.get(
                'https://www.instagram.com/api/v1/users/web_profile_info/?username=crictracker',
                headers=headers,
                proxy=None,  # Set to None if not using proxy
                impersonate="chrome110"            # Browser fingerprint
            )
    print(response.status_code)
    print(response.text)
    await session.close()
    return response

# This is how you run the async function
if __name__ == "__main__":
    asyncio.run(fetch_profile())
