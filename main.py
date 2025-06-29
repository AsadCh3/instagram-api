import json
import aiohttp
from fastapi import FastAPI, Query, HTTPException, Request
import uvicorn
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from config import USER_API, USER_HEADERS, DEFAULT_HEADERS


# proxy_url = 'http://5.79.73.131:13080'


cookies = {
    'csrftoken': '8adqd4hXu6O3vCjNO4okm5MfcstV6CEM',
    'ds_user_id': '48647407443',
    'sessionid': '48647407443%3ApqWFAMLoWJWfWB%3A26%3AAYchyDXj6jQMqj8b79OX4kmjH5pRoY5yAfdrpnXWmQ'
}


headers = {
    'x-csrftoken': '8adqd4hXu6O3vCjNO4okm5MfcstV6CEM',
    'x-ig-app-id': '936619743392459'
}


# API key configuration
API_KEY = "GdvRcHsnngHejPKGxJfafhbCrCKFsPogwTCVCSTpScORMJjIus"

# Create limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Post Crawler API",
    description="API to crawl post details",
    version="1.0.0"
)

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


async def get_post(post_short_code, session):
    """
    Crawl and Parse Instagram Post data and extract profile information asynchronously.

    Args:
    post_short_code (str): string containing Post ID

    Returns:
    dict: Dictionary containing extracted profile information and Post Information
    """

    POST_API = "https://www.instagram.com/graphql/query"
    PAYLOAD = 'fb_api_caller_class=RelayModern&fb_api_req_friendly_name=PolarisPostActionLoadPostQueryQuery&variables=%7B%22shortcode%22%3A%22{}%22%2C%22fetch_tagged_user_count%22%3Anull%2C%22hoisted_comment_id%22%3Anull%2C%22hoisted_reply_id%22%3Anull%7D&server_timestamps=true&doc_id=8845758582119845'

    async with session.post(
        POST_API,
        headers=headers,
        data=PAYLOAD.format(post_short_code),
        # proxy=proxy_url,
        cookies=cookies,
        ssl=False
    ) as response:

        if response.status == 200:
            response_data = await response.json()
            return response_data

        return {'details': 'status code not good', 'status': response.status}


@app.get("/api/post", tags=["Posts"])
@limiter.limit("200 per second")
async def crawl_posts(
        request: Request,
        post_short_code: str = Query(..., description="Post ID to crawl the post details"),
        key: str = Query(..., description="API key for authentication")
):
    """
    Retrieve post data using the post short code

    Returns:
        JSON with post details
    """
    # Check API key
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    if not post_short_code:
        raise HTTPException(status_code=400, detail="post_short_code is required")

    try:
        post_data = await get_post(post_short_code=post_short_code, session=session)
        return post_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/followers", tags=["Followers"])
async def crawl_followers(
        request: Request,
        username: str,
        key: str = Query(..., description="API key for authentication")
):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    user_id = await get_userid(username)

    if not 'user_id' in user_id:
        return {"details": "User no found.", "status": 404}

    INSTAGRAM_FOLLOWERS_API = f"https://www.instagram.com/api/v1/friendships/{user_id['user_id']}/followers/"

    params = {
        'count': '12',
        'search_surface': 'follow_list_page',
    }

    async with session.get(
        INSTAGRAM_FOLLOWERS_API,
        params=params,
        # proxy=proxy_url,
        headers=headers,
        cookies=cookies,
        ssl=False
    ) as response:
        if not response.ok:
            return {"error": "Failed to fetch data from Instagram", "status_code": response.status}

        data = await response.json()
        return data


@app.get("/api/following", tags=["Following"])
async def get_following(
    request: Request,
    username: str,
    key: str = Query(..., description="API key for authentication")
):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    user_id = await get_userid(username)

    if not 'user_id' in user_id:
        return {"details": "User no found.", "status": 404}

    INSTAGRAM_FOLLOWERS_API = f"https://www.instagram.com/api/v1/friendships/{user_id['user_id']}/following/"

    params = {
        'count': '12',
        'search_surface': 'follow_list_page',
    }

    async with session.get(
        INSTAGRAM_FOLLOWERS_API,
        params=params,
        # proxy=proxy_url,
        headers=headers,
        cookies=cookies,
        ssl=False
    ) as response:
        if not response.ok:
            return {"error": "Failed to fetch data from Instagram", "status_code": response.status}

        data = await response.json()
        return data


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

    async with session.post(
        'https://www.instagram.com/ajax/bulk-route-definitions/',
        headers=headers,
        data=data,
        # proxy=proxy_url,
        ssl=False
    ) as response:

        response_text = await response.text()

        print("response_text:...", response_text)

        try:
            data = json.loads(response_text[9:])
            try:
                return {
                    'user_id': data['payload']['payloads'][f'/{username}/']['result']['exports']['rootView']['props']['id']
                }
            except:
                raise HTTPException(
                    status_code=404,
                    detail="User does not exist",
                )
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail="Instagram returned malformed JSON",
            )


@app.get('/api/userinfo', tags=["Following"])
async def crawl_userinfo_partial(
    request: Request,
    username: str,
    key: str = Query(..., description="API key for authentication")
):

    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    INSTAGRAM_GRAPHQL_URL = "https://www.instagram.com/graphql/query"
    DOC_ID = "10068642573147916"

    user_id_dic = await get_userid(username=username)
    user_id = user_id_dic.get('user_id')

    if not user_id:
        return {'message': 'username not found'}

    data = {
        'variables': f'{{"id":"{user_id}","render_surface":"PROFILE"}}',
        'doc_id': DOC_ID,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            INSTAGRAM_GRAPHQL_URL,
            headers=headers,
            cookies=cookies,
            # proxy=proxy_url,
            data=data,
            ssl=False
        ) as resp:
            response = await resp.json()
            return response


@app.get('/api/userdetails')
async def crawl_userinfo_complete(
    request: Request,
    username: str,
    key: str = Query(..., description="API key for authentication")
):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    session.cookie_jar.clear()

    async with session.get(
        "https://www.instagram.com/",
        headers=DEFAULT_HEADERS,
        # proxy=proxy_url,
        ssl=False
    ) as outer_response:
        content = await outer_response.text()
        csrf_token = content.split('"csrf_token":"')[-1].split('"')[0]
        USER_HEADERS['Cookie'] = 'csrftoken={}'.format(csrf_token)
        session.cookie_jar.clear()

        async with session.get(
            USER_API.format(username),
            headers=USER_HEADERS,
            # proxy=proxy_url,
            ssl=False
        ) as response:
            response_data = await response.json()
            user_data = response_data['data']['user']
            data = {}
            data['biography'] = user_data['biography']
            data['bio_links'] = user_data['bio_links']
            data['fb_profile_biolink'] = user_data['fb_profile_biolink']
            data['post_count'] = len(user_data['edge_owner_to_timeline_media']['edges'])
            data['followers_count'] = user_data['edge_followed_by']['count']
            data['follow_count'] = user_data['edge_follow']['count']
            data['full_name'] = user_data['full_name']
            data['id'] = user_data['id']
            data['category_name'] = user_data['category_name']
            data['profile_pic_url'] = user_data['profile_pic_url_hd']
            for key in ('edge_felix_video_timeline', 'edge_owner_to_timeline_media', 'edge_related_profiles'):
                response_data['data']['user'].pop(key, None)
            data['raw_data'] = response_data
            return data


@app.get('/api/relatedprofiles')
async def crawl_userinfo_complete(
    request: Request,
    username: str,
    key: str = Query(..., description="API key for authentication")
):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    session.cookie_jar.clear()

    async with session.get(
        "https://www.instagram.com/",
        headers=DEFAULT_HEADERS,
        # proxy=proxy_url,
        ssl=False
    ) as outer_response:
        content = await outer_response.text()
        csrf_token = content.split('"csrf_token":"')[-1].split('"')[0]
        USER_HEADERS['Cookie'] = 'csrftoken={}'.format(csrf_token)
        session.cookie_jar.clear()

        async with session.get(
            USER_API.format(username),
            headers=USER_HEADERS,
            # proxy=proxy_url,
            ssl=False
        ) as response:
            data = await response.json()
            return data['data']['user']['edge_related_profiles']


@app.get('/api/posts')
async def get_posts(
    request: Request,
    username: str,
    key: str = Query(..., description="API key for authentication")
):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    userid_response = await get_userid(username)
    if not 'user_id' in userid_response:
        return userid_response, 400

    data = {
        'variables': '{"data":{"count":15,"include_reel_media_seen_timestamp":true,"include_relationship_info":true,"latest_besties_reel_media":true,"latest_reel_media":true},"username":"%s","__relay_internal__pv__PolarisIsLoggedInrelayprovider":true,"__relay_internal__pv__PolarisShareSheetV3relayprovider":true}' % username,
        'doc_id': '9654017011387330',
    }

    async with session.post(
            'https://www.instagram.com/graphql/query', 
            headers=headers, 
            cookies=cookies, 
            data=data,
            # proxy=proxy_url,
            ssl=False
        ) as response:

        result = await response.json()

        edges = result['data']['xdt_api__v1__feed__user_timeline_graphql_connection']['edges']

        cleaned_edges = []

        userid = userid_response['user_id']
        for edge in edges:
            if userid not in edge['node']['timeline_pinned_user_ids']:
                cleaned_edges.append(edge)

        result['data']['xdt_api__v1__feed__user_timeline_graphql_connection']['edges'] = cleaned_edges
        return result


@app.get('/api/reels')
async def get_reels(
    request: Request,
    username: str,
    key: str = Query(..., description="API key for authentication")
):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    user_id_dic = await get_userid(username=username)
    user_id = user_id_dic.get('user_id')

    if not user_id:
        return {'message': 'username not found'}

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
        proxy=proxy_url,
        ssl=False
    ) as response:
        response = await response.json()
        return response


@app.get('/api/likers_comments')
async def likers_comments(
    request: Request,
    username: str,
    key: str = Query(..., description="API key for authentication")
):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    # call internal api to get posts ids
    posts = await get_posts(
        request=None, 
        username=username, 
        key=key
    )
    post_id_1 = posts['data']['xdt_api__v1__feed__user_timeline_graphql_connection']['edges'][0]['node']['pk']
    post_id_2 = posts['data']['xdt_api__v1__feed__user_timeline_graphql_connection']['edges'][1]['node']['pk']
    post_id_3 = posts['data']['xdt_api__v1__feed__user_timeline_graphql_connection']['edges'][2]['node']['pk']

    async with session.get(
        f'https://www.instagram.com/api/v1/media/{post_id_1}/likers/', 
        cookies=cookies, 
        headers=headers,
        ssl=False
    ) as response:
        response = await response.json()
        print(response)
        likers_1 = response

    async with session.get(
        f'https://www.instagram.com/api/v1/media/{post_id_2}/likers/', 
        cookies=cookies, 
        headers=headers,
        ssl=False
    ) as response:
        response = await response.json()
        likers_2 = response

    async with session.get(
        f'https://www.instagram.com/api/v1/media/{post_id_3}/likers/',
        cookies=cookies,
        headers=headers,
        ssl=False
    ) as response:
        response = await response.json()
        likers_3 = response

    likers = [likers_1['users'], likers_2['users'], likers_3['users']]

    data = {
        'fb_api_caller_class': 'RelayModern',
        'fb_api_req_friendly_name': 'PolarisPostCommentsContainerQuery',
        'server_timestamps': 'true',
        'doc_id': '29789987647283145',
    }

    data['variables'] = '{"media_id":"%s","__relay_internal__pv__PolarisIsLoggedInrelayprovider":true}' % post_id_1

    async with session.post(
        'https://www.instagram.com/graphql/query', 
        cookies=cookies, 
        headers=headers, 
        data=data,
        ssl=False
    ) as response:
        response = await response.json()
        comments_1 = response['data']['xdt_api__v1__media__media_id__comments__connection']['edges']

    data['variables'] = '{"media_id":"%s","__relay_internal__pv__PolarisIsLoggedInrelayprovider":true}' % post_id_2

    async with session.post(
        'https://www.instagram.com/graphql/query', 
        cookies=cookies, 
        headers=headers, 
        data=data,
        ssl=False
    ) as response:
        response = await response.json()
        comments_2 = response['data']['xdt_api__v1__media__media_id__comments__connection']['edges']

    data['variables'] = '{"media_id":"%s","__relay_internal__pv__PolarisIsLoggedInrelayprovider":true}' % post_id_3

    async with session.post(
        'https://www.instagram.com/graphql/query', 
        cookies=cookies, 
        headers=headers, 
        data=data,
        ssl=False
    ) as response:
        response = await response.json()
        comments_3 = response['data']['xdt_api__v1__media__media_id__comments__connection']['edges']

    comments = [comments_1, comments_2, comments_3]

    return {'likers': likers, 'comments': comments}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
