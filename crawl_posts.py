import math
import datetime
import random
import aiohttp
import asyncio
from config import *

async def get_post(post_short_code, session):
    """
    Crawl and Parse Instagram Post data and extract profile information asynchronously.

    Args:
    post_short_code (str): string containing Post ID

    Returns:
    dict: Dictionary containing extracted profile information and Post Information
    """

    proxy_url = 'http://7d7fb05e627d22dd9e61:d14574526ec931a6@gw.dataimpulse.com:823'

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.instagram.com',
        'priority': 'u=1, i',
        'referer': 'https://www.instagram.com/apple/',
        'sec-ch-prefers-color-scheme': 'dark',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-full-version-list': '"Google Chrome";v="135.0.7049.115", "Not-A.Brand";v="8.0.0.0", "Chromium";v="135.0.7049.115"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-model': '"Nexus 5"',
        'sec-ch-ua-platform': '"Android"',
        'sec-ch-ua-platform-version': '"6.0"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36',
        'x-asbd-id': '359341',
        'x-bloks-version-id': '446750d9733aca29094b1f0c8494a768d5742385af7ba20c3e67c9afb91391d8',
        'x-csrftoken': 'uJ2xECzzB4GkWgi07L1jnLiKVmYx9jnj',
        'x-fb-friendly-name': 'PolarisProfilePageContentQuery',
        'x-fb-lsd': '7sbE35jhEuyOkX2JpcL36s',
        'x-ig-app-id': '1217981644879628',
        'x-root-field-name': 'fetch__XDTUserDict'
    }

    cookies = {
        'fbm_124024574287414': 'base_domain=.instagram.com',
        'datr': 'lMGKZpDUbrYL2RLJrt8KBYn2',
        'mid': 'ZpE-VAAEAAEktdGRmyH3FjNS7HLp',
        'ig_did': 'F482767C-4401-4006-9683-1C67AF0481FC',
        'ig_nrcb': '1',
        'ps_l': '1',
        'ps_n': '1',
        'csrftoken': 'uJ2xECzzB4GkWgi07L1jnLiKVmYx9jnj',
        'ds_user_id': '48647407443',
        'sessionid': '48647407443%3AF9a0cv88JMP1pn%3A7%3AAYeAJWSXLv0cKJhLDvFaHmljonwk5gFyPq_xFvLKuBw',
        'rur': '"LDC\\05448647407443\\0541777808220:01f77f66c4eb3dd79e904536ca52a3af451e653dc861915349f480766ea60150131bd9bb"',
        'wd': '684x691',
    }

    async with session.post(
        POST_API,
        headers=headers,
        data=PAYLOAD.format(post_short_code),
        proxy=proxy_url,
        cookies=cookies,
        ssl=False
    ) as response:
        response_status = response.status

        print(await response.text())

        if response_status == 200:
            response_data = await response.json()
            return response_data

        return {'details': 'status code not good', 'status': response_status}


headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'priority': 'u=1, i',
    'referer': 'https://www.instagram.com/kashffali02/followers/',
    'sec-ch-prefers-color-scheme': 'dark',
    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="135.0.7049.96", "Not-A.Brand";v="8.0.0.0", "Chromium";v="135.0.7049.96"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-model': '"Nexus 5"',
    'sec-ch-ua-platform': '"Android"',
    'sec-ch-ua-platform-version': '"6.0"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36',
    'x-asbd-id': '359341',
    'x-csrftoken': 'uJ2xECzzB4GkWgi07L1jnLiKVmYx9jnj',
    'x-ig-app-id': '1217981644879628',
    'x-ig-www-claim': 'hmac.AR2rqkQP1dG8TEMqBlom2ioxu57KG5tZp1yMA8ptOCSUUywK',
    'x-requested-with': 'XMLHttpRequest',
    'x-web-session-id': '6lfp4l:pquktf:c4mllg'
}

async def fetch_followers_page(user_id, session, max_id=None):
    timeout = aiohttp.ClientTimeout(total=10)
    params = {
        'count': '12',
        'search_surface': 'follow_list_page',
    }
    if max_id:
        params['max_id'] = max_id

    async with session.get(
        f'https://www.instagram.com/api/v1/friendships/{user_id}/followers/',
        headers=headers,
        timeout=timeout,
        params=params,
        ssl=False
    ) as response:
        data = await response.json()
        return data

async def get_followers(user_id, follower_count, session):
    users = []
    max_id = None
    batch_size = 5  # Number of requests in parallel per batch

    total_pages = math.ceil(follower_count / 12)

    while total_pages > 0:
        tasks = []

        for _ in range(min(batch_size, total_pages)):
            task = asyncio.create_task(fetch_followers_page(user_id, session, max_id))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        for data in results:
            users += data['users']
            max_id = data.get('next_max_id')
            if not max_id:
                break

        total_pages -= batch_size

        if not max_id:
            break  # No more pages to fetch

    print(f"Fetched {len(users)} followers")
    return users


async def fetch_following_page(user_id, session, max_id=None):
    timeout = aiohttp.ClientTimeout(total=10)
    params = {
        'count': '12',
        'search_surface': 'follow_list_page',
    }
    if max_id:
        params['max_id'] = max_id

    async with session.get(
        f'https://www.instagram.com/api/v1/friendships/{user_id}/following/',
        headers=headers,
        timeout=timeout,
        params=params,
        ssl=False
    ) as response:
        data = await response.json()
        return data

async def get_following(user_id, follower_count, session):
    users = []
    max_id = None
    batch_size = 5  # Number of requests in parallel per batch

    total_pages = math.ceil(follower_count / 12)

    while total_pages > 0:
        tasks = []

        for _ in range(min(batch_size, total_pages)):
            task = asyncio.create_task(fetch_following_page(user_id, session, max_id))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        for data in results:
            users += data['users']
            max_id = data.get('next_max_id')
            if not max_id:
                break

        total_pages -= batch_size

        if not max_id:
            break  # No more pages to fetch

    print(f"Fetched {len(users)} followers")
    return users
