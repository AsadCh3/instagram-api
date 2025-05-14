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
    max_retries = 2
    retry_count = 0

    while retry_count <= max_retries:
        try:
            # Set a timeout to avoid hanging requests
            timeout = aiohttp.ClientTimeout(total=10)

            proxy_url = 'http://7d7fb05e627d22dd9e61:d14574526ec931a6@gw.dataimpulse.com:823'

            async with session.post(
                    POST_API,
                    headers=DEFAULT_HEADERS,
                    data=PAYLOAD.format(post_short_code),
                    proxy = proxy_url,
                    timeout=timeout,
                    ssl=False
            ) as response:
                response_status = response.status

                if response_status == 200:
                    response_text = await response.json()

                    if not response_text['data']['xdt_shortcode_media']:
                        return {'status': 404, 'message': 'Post Not Found'}
                    response = response_text
                    xdt_shortcode_media = response['data']['xdt_shortcode_media']
                    try:
                        caption = xdt_shortcode_media['edge_media_to_caption']['edges'][0]['node']['text']
                        caption = caption.encode().decode('unicode_escape')
                    except Exception as e:
                        caption = ''
                    if caption == '':
                        caption = None
                    try:
                        created_at = xdt_shortcode_media['edge_media_to_caption']['edges'][0]['node']['created_at']
                    except Exception as e:
                        created_at = None
                    if created_at:
                        created_at = datetime.datetime.fromtimestamp(int(created_at))
                    post_id = xdt_shortcode_media['id']

                    # Parse Commands
                    command_count = xdt_shortcode_media['edge_media_to_parent_comment']['count']
                    commands = []
                    commands_json = xdt_shortcode_media['edge_media_to_parent_comment']['edges']
                    for command_dict in commands_json:
                        command_dict = command_dict['node']
                        commands.append({'command_text': command_dict['text'].encode().decode('unicode_escape'),
                                         'created_at': command_dict['created_at'],
                                         'command_likes': command_dict['edge_liked_by']['count'],
                                         'commander_user_name': command_dict['owner']['username']})

                    # Likes
                    edge_media_preview_like = xdt_shortcode_media['edge_media_preview_like']['count']

                    # Owner Info
                    owner_user_name = xdt_shortcode_media['owner']['username']
                    owner_id = xdt_shortcode_media['owner']['id']
                    owner_is_verified = xdt_shortcode_media['owner']['is_verified']
                    owner_profile_pic_url = xdt_shortcode_media['owner']['profile_pic_url']
                    owner_full_name = xdt_shortcode_media['owner']['full_name']
                    owner_is_private = xdt_shortcode_media['owner']['is_private']
                    owner_post_count = xdt_shortcode_media['owner']['edge_owner_to_timeline_media']['count']
                    owner_followed_by = xdt_shortcode_media['owner']['edge_followed_by']['count']

                    shortcode = xdt_shortcode_media['shortcode']
                    if xdt_shortcode_media['is_video']:
                        url = f'https://www.instagram.com/reel/{shortcode}'
                    else:
                        url = f'https://www.instagram.com/p/{shortcode}'

                    # Video Info
                    video_view_count = None
                    video_play_count = None
                    title = None
                    video_duration = None
                    video_url = None
                    attached_images = []
                    if xdt_shortcode_media['is_video']:
                        video_view_count = xdt_shortcode_media['video_view_count']
                        video_play_count = xdt_shortcode_media['video_play_count']
                        title = xdt_shortcode_media['title']
                        video_duration = xdt_shortcode_media['video_duration']
                        video_url = xdt_shortcode_media['video_url']
                    else:
                        try:
                            display_resources = xdt_shortcode_media['edge_sidecar_to_children']['edges']
                            if display_resources:
                                attached_images = [img['node']['display_url'] for img in display_resources]
                        except Exception as e:
                            attached_images = [xdt_shortcode_media['display_url']]

                    post_data = {'alt': xdt_shortcode_media['accessibility_caption'],
                                 'user_id': owner_id,
                                 'username': owner_user_name,
                                 'product_type': 'feed',
                                 'short_code': shortcode,
                                 'video_url': video_url,
                                 'video_view_count': video_view_count,
                                 'video_play_count': video_play_count,
                                 'video_duration': video_duration,
                                 'post_date': created_at,
                                 'sponsor_user': xdt_shortcode_media['edge_media_to_sponsor_user']['edges'],
                                 'owner': xdt_shortcode_media['owner'],
                                 'is_affiliate': xdt_shortcode_media['is_affiliate'],
                                 'is_paid_partnership': xdt_shortcode_media['is_paid_partnership'],
                                 'is_ad': xdt_shortcode_media['is_ad'],
                                 'latest_comments': [command['node'] for command in xdt_shortcode_media['edge_media_preview_comment']['edges']],
                                 'category': None,
                                 'owner_is_verified': owner_is_verified,
                                 'owner_profile_pic_url': owner_profile_pic_url,
                                 'owner_full_name': owner_full_name,
                                 'owner_is_private': owner_is_private,
                                 'owner_post_count': owner_post_count,
                                 'owner_followed_by': owner_followed_by,
                                 'post_id': post_id,
                                 'post_url': url,
                                 'caption': caption,
                                 'like_count': edge_media_preview_like,
                                 'command_count': command_count,
                                 'command_preview': commands,
                                 'video_info': {'video_view_count': video_view_count,
                                                'video_play_count': video_play_count,
                                                'video_duration': video_duration,
                                                'video_title': title,
                                                'video_url': video_url},
                                 'attached_images': attached_images
                                 }
                    return post_data
                else:
                    # If we've reached max retries, return error
                    if retry_count >= max_retries:
                        return {'status': 400, 'message': 'Failed To Fetch'}
                    retry_count += 1

        except Exception as e:
            # If we've reached max retries, return error
            if retry_count >= max_retries:
                return {'status': 500, 'message': f'Error: {str(e)}'}

            # Otherwise increment retry counter and try again
            retry_count += 1
            await asyncio.sleep(0.5)  # Short delay between retries


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
