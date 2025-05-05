import json
import aiohttp
from fastapi import FastAPI, Query, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import uvicorn
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from crawl_posts import get_post
from crawl_users import get_user
from crawl_posts import get_followers, get_following
import requests
import asyncio
from typing import List
from pydantic import BaseModel
from config import USER_API, USER_HEADERS, DEFAULT_HEADERS

# proxy_url = "http://geonode_kKSipeCuCI-type-residential:74280c0b-289f-4e55-a924-4008703dabda@proxy.geonode.io:9000"
proxy_url = 'http://7d7fb05e627d22dd9e61:d14574526ec931a6@gw.dataimpulse.com:823'

# API key configuration
API_KEY = "J2pQvkrA75KtrVHpKuc41XqLON4pyw2ilO6beOYhJiLxHbnE3V"

# Create limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Post Crawler API",
              description="API to crawl post details",
              version="1.0.0")

# Add rate limiter to FastAPI
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Create a single session for reuse across requests
session = None


async def get_session():
    global session
    if session is None or session.closed:
        session = aiohttp.ClientSession()
    return session


async def close_session():
    global session
    if session and not session.closed:
        await session.close()


@app.on_event("startup")
async def startup_event():
    await get_session()


@app.on_event("shutdown")
async def shutdown_event():
    await close_session()


# @app.get("/api/posts", tags=["Posts"])
# @limiter.limit("200 per second")
# async def crawl_posts(
#         request: Request,
#         post_short_code: str = Query(..., description="Post ID to crawl the post details"),
#         # key: str = Query(..., description="API key for authentication")
# ):
#     """
#     Retrieve post data using the post short code

#     Returns:
#         JSON with post details
#     """
    # Check API key
    # if key != API_KEY:
    #     raise HTTPException(status_code=403, detail="Invalid API key")

    # if not post_short_code:
    #     raise HTTPException(status_code=400, detail="post_short_code is required")

    # try:
    #     post_data = await get_post(post_short_code=post_short_code, session=session)
    #     return post_data
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


# @app.get("/api/users", tags=["Users"])
# @limiter.limit("200 per second")
# async def crawl_users(
#         request: Request,
#         user_id: str = Query(..., description="User ID to crawl the user details"),
#         # key: str = Query(..., description="API key for authentication")
# ):
#     """
#     Retrieve user data using the user id

#     Returns:
#         JSON with post details
#     """
#     # Check API key
#     # if key != API_KEY:
#     #     raise HTTPException(status_code=403, detail="Invalid API key")

#     if not user_id:
#         raise HTTPException(status_code=400, detail="user_id is required")

#     try:
#         user_data = await get_user(user_id=user_id, session=session)
#         return user_data
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/api/followers", tags=["Followers"])
# async def crawl_followers(
#         request: Request,
#         user_id: int
# ):
#     INSTAGRAM_GRAPHQL_URL = "https://www.instagram.com/graphql/query"
#     DOC_ID = "10068642573147916"

#     data = {
#         'variables': f'{{"id":"{user_id}","render_surface":"PROFILE"}}',
#         'doc_id': DOC_ID,
#     }

#     response = requests.post(INSTAGRAM_GRAPHQL_URL, data=data)

#     if response.status_code != 200:
#         return {"error": "Failed to fetch data from Instagram", "status_code": response.status_code}

#     return response.json()


async def get_userid(username):
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
        'x-fb-lsd': 'awHBVkAcim8ZZGDUF0jLHX',
        'x-ig-d': 'www'
    }

    data = f'route_urls[0]=%2F{username}%2F&routing_namespace=igx_www%24a%2487a091182d5bd65bcb043a2888004e09&__d=www&__user=0&__a=1&__req=9&__hs=20213.HYP%3Ainstagram_web_pkg.2.1...1&dpr=2&__ccg=POOR&__rev=1022515417&__s=pa6mmy%3Aqgmc8c%3A2dr157&__hsi=7501024739781509948&__dyn=7xe5WwlEnwn8K2Wmm1twpUnwgU7S6EdF8aUco38w5ux609vCwjE1EE2Cw8G11wBw5Zx62G3i1ywOwa90Fw4Hw9O0Lbwae4UaEW2G0AEco5G0zEnwhE0za2-azo7u1xwIwbS1LwTwKG1pg2Xwr86C1mwrd6goK10xKi2K7E5y4U4u0P8K6U16Usw&__csr=hL1NNIn9dsAYIAl9t8Ky96aG9BWWRsLitlIMyG-jKiBgxBzGGiF9kAeAz8RN2C9jGF9aAK9WWhbVpeBQESGV9eXVK-q5oSiqRyVogVHmjGbSiueVkfFVeWBypGy-uiaz4i9KehVkQeAGbKuUB2Z1a9ze-uu8QECq4EyWx9AzXLQfCyUiCCwxyUyq5801iTcw0KmfzU15o8o7Kl1_w4mU1CU46E5-04Xo0hRgapYw6C0y8lwaK8DG9wCwEhhwy0b5wauywgE19IEdU4i4okUZ3lg8ocNpAaBh8-aUuCwppQ10o7e0bJwjUe87k-u1DD-6NxkaCw0qRU1VU0_q&__hsdp=l0MMyTjdl_7h2FihcjoAAayVojJ396oigoho4u2WlZaEkgCnzxVCV2m1I50xzE7JAxK36dEw98y366lx57Kexm3i2a4S7U4m2O2e18wGxW4EdXwiE98nwkUG12wCyU0z-7o1DU10U9U3ew8W1Yxh0b6682xwvE2Gwcy3G2bg8o3dx-13of8W5E6Ci18GfwhU8U4C3UUizEbo&__hblpi=0fW0To3Xwfa2m8wjEhhXzElwlUdo4m2O2e18wGxW4EdXwiE98nwkUG12wCyU0z-7o1DU10U9U3ew8W1Yxh0b6682xwvE2Gwcy3G2bg8o3dx-13of8W5E6W1rwhU8U4C3UUizEbo&__hblpn=0mUeU4y0ZE3HwoUtz89EW19wZxu36UmxC2mm1GwBzEy9DxF0EwLwQzozx20iO3qi0um1vUfo15o4C0IE25wdy221NwPw9G6E4S0iO0b1yFo6i6olwZwXwBwBwwAwqE6a3W78bA48&__comet_req=7&fb_dtsg=NAcO-mMWDD318VJtOxuQgwjjiLwwtM9u2iMNLgfYCk5zOMC0hpBdeyg%3A17855905060073950%3A1746274676&jazoest=26363&lsd=awHBVkAcim8ZZGDUF0jLHX&__spin_r=1022515417&__spin_b=trunk&__spin_t=1746468418&__crn=comet.igweb.PolarisProfilePostsTabRoute'

    response = requests.post('https://www.instagram.com/ajax/bulk-route-definitions/', headers=headers, data=data)

    print(response.status_code)

    data = json.loads(response.text[9:])

    try:
        return {
            'user_id': data['payload']['payloads'][f'/{username}/']['result']['exports']['rootView']['props']['id']
        }
    except:
        return {}


@app.get('/api/userinfo', tags=["Following"])
async def crawl_userinfo_partial(
    request: Request,
    username: str
):
    INSTAGRAM_GRAPHQL_URL = "https://www.instagram.com/graphql/query"
    DOC_ID = "10068642573147916"

    user_id_dic = await get_userid(username=username)
    user_id = user_id_dic.get('user_id')

    if not user_id:
        return {'message': 'username not found'}

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

    data = {
        'variables': f'{{"id":"{user_id}","render_surface":"PROFILE"}}',
        'doc_id': DOC_ID,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            INSTAGRAM_GRAPHQL_URL,
            headers=headers,
            cookies=cookies,
            data=data,
            ssl=False
        ) as resp:
            response = await resp.json()
            return response


@app.get('/api/userdetails')
async def crawl_userinfo_complete(
    request: Request,
    username: str
):
    session.cookie_jar.clear()

    async with session.get(
        "https://www.instagram.com/",
        headers=DEFAULT_HEADERS,
        proxy=None,
        ssl=False
    ) as outer_response:
        content = await outer_response.text()
        csrf_token = content.split('"csrf_token":"')[-1].split('"')[0]
        USER_HEADERS['Cookie'] = 'csrftoken={}'.format(csrf_token)
        session.cookie_jar.clear()

        async with session.get(
            USER_API.format(username),
            headers=USER_HEADERS,
            proxy=proxy_url,
            ssl=False
        ) as response:
            print(response.status)
            data = await response.json()
            for key in ('edge_felix_video_timeline', 'edge_owner_to_timeline_media', 'edge_related_profiles'):
                data['data']['user'].pop(key, None)
            return data


@app.get('/api/relatedprofiles')
async def crawl_userinfo_complete(
    request: Request,
    username: str
):
    session.cookie_jar.clear()

    async with session.get(
        "https://www.instagram.com/",
        headers=DEFAULT_HEADERS,
        proxy=None,
        ssl=False
    ) as outer_response:
        content = await outer_response.text()
        csrf_token = content.split('"csrf_token":"')[-1].split('"')[0]
        USER_HEADERS['Cookie'] = 'csrftoken={}'.format(csrf_token)
        session.cookie_jar.clear()

        async with session.get(
            USER_API.format(username),
            headers=USER_HEADERS,
            proxy=proxy_url,
            ssl=False
        ) as response:
            print(response.status)
            data = await response.json()
            return data['data']['user']['edge_related_profiles']


@app.get('/api/posts')
async def get_posts(
    request: Request,
    username: str
):

    cookies = {
        'fbm_124024574287414': 'base_domain=.instagram.com',
        'datr': 'lMGKZpDUbrYL2RLJrt8KBYn2',
        'mid': 'ZpE-VAAEAAEktdGRmyH3FjNS7HLp',
        'ig_did': 'F482767C-4401-4006-9683-1C67AF0481FC',
        'ig_nrcb': '1',
        'ps_l': '1',
        'ps_n': '1',
        'wd': '1440x778',
        'csrftoken': 'uJ2xECzzB4GkWgi07L1jnLiKVmYx9jnj',
        'ds_user_id': '48647407443',
        'sessionid': '48647407443%3AgkIuttIqmS8jTy%3A5%3AAYdSlaSHDdxGuuiJg9Iz5nXwJur7wypFLpWwyY02_w',
        'rur': '"LDC\\05448647407443\\0541777810946:01f731210f707148540c301acfadea255114c1f66bb27c939f4bca74a7537a8347864ae3"'
    }

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
        'x-fb-friendly-name': 'PolarisProfilePostsQuery',
        'x-fb-lsd': 'PfG09UjH9yXHHNpBLfXNnU',
        'x-ig-app-id': '1217981644879628',
        'x-root-field-name': 'xdt_api__v1__feed__user_timeline_graphql_connection'
    }

    data = {
        'variables': '{"data":{"count":15,"include_reel_media_seen_timestamp":true,"include_relationship_info":true,"latest_besties_reel_media":true,"latest_reel_media":true},"username":"%s","__relay_internal__pv__PolarisIsLoggedInrelayprovider":true,"__relay_internal__pv__PolarisShareSheetV3relayprovider":true}' % username,
        'doc_id': '9654017011387330',
    }

    response = requests.post(
        'https://www.instagram.com/graphql/query',
        headers=headers,
        cookies=cookies,
        data=data
    )
    return response.json()


@app.get('/api/reels')
async def get_posts(
    request: Request,
    username: str
):
    
    user_id_dic = await get_userid(username=username)
    user_id = user_id_dic.get('user_id')

    if not user_id:
        return {'message': 'username not found'}

    cookies = {
        'fbm_124024574287414': 'base_domain=.instagram.com',
        'datr': 'lMGKZpDUbrYL2RLJrt8KBYn2',
        'mid': 'ZpE-VAAEAAEktdGRmyH3FjNS7HLp',
        'ig_did': 'F482767C-4401-4006-9683-1C67AF0481FC',
        'ig_nrcb': '1',
        'ps_l': '1',
        'ps_n': '1',
        'wd': '1440x778',
        'csrftoken': 'uJ2xECzzB4GkWgi07L1jnLiKVmYx9jnj',
        'ds_user_id': '48647407443',
        'sessionid': '48647407443%3AgkIuttIqmS8jTy%3A5%3AAYdSlaSHDdxGuuiJg9Iz5nXwJur7wypFLpWwyY02_w',
        'rur': '"LDC\\05448647407443\\0541777810731:01f70fbbc6e948b47bb7cec7369ffecc80a8dac9dbd26161febece10381681f64561e19b"',
    }

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
        'x-fb-friendly-name': 'PolarisProfileReelsTabContentQuery',
        'x-fb-lsd': '7sbE35jhEuyOkX2JpcL36s',
        'x-ig-app-id': '1217981644879628',
        'x-root-field-name': 'xdt_api__v1__clips__user__connection_v2',
    }

    data = {
        'variables': '{"data":{"include_feed_video":true,"page_size":15,"target_user_id":"%s"}}' % user_id,
        'server_timestamps': 'true',
        'doc_id': '29938381755760668',
    }

    async with session.post(
        'https://www.instagram.com/graphql/query',
        headers=headers,
        data=data,
        cookies=cookies,
        ssl=False
    ) as response:
        response = await response.json()
        return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
