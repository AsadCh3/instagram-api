import random
import datetime
import aiohttp
import asyncio
from config import *


async def get_user(user_id, session):
    """
    Crawl and Parse Instagram Post data and extract profile information asynchronously.

    Args:
    post_short_code (str): string containing Post ID

    Returns:
    dict: Dictionary containing extracted profile information and Post Information
    """
    max_retries = 7
    retry_count = 0

    while retry_count <= max_retries:
        try:
            # Set a timeout to avoid hanging requests
            session.cookie_jar.clear()
            timeout = aiohttp.ClientTimeout(total=10)

            proxy_url = "http://geonode_kKSipeCuCI-type-residential:74280c0b-289f-4e55-a924-4008703dabda@proxy.geonode.io:9000"
            
            async with session.get(
                    "https://www.instagram.com/",
                    headers=DEFAULT_HEADERS,
                    proxy=None,
                    timeout=timeout,
                    ssl=False
            ) as outer_response:
                content = await outer_response.text()
                csrf_token = content.split('"csrf_token":"')[-1].split('"')[0]
                USER_HEADERS['Cookie'] = 'csrftoken={}'.format(csrf_token)
                print(USER_HEADERS)
                session.cookie_jar.clear()
                async with session.get(
                        USER_API.format(user_id),
                        headers=USER_HEADERS,
                        # proxy=proxy_url,
                        timeout=timeout,
                        ssl=False
                ) as response:
                    response_status = response.status
                    print(response.status)
                    response = await response.json()
                    # print(response)
                    if response_status == 200:
                        data = {}
                        user_data = response['data']['user']
                        data['user_id'] = user_id
                        data['biography'] = user_data['biography']
                        data['bio_links'] = user_data['bio_links']
                        data['fb_profile_biolink'] = user_data['fb_profile_biolink']
                        data['followers_count'] = user_data['edge_followed_by']['count']
                        data['follow_count'] = user_data['edge_follow']['count']
                        data['full_name'] = user_data['full_name']
                        data['id'] = user_data['id']
                        data['category_name'] = user_data['category_name']
                        data['profile_pic_url'] = user_data['profile_pic_url_hd']
                        data['posts'] = []
                        data['raw_data'] = response
                        posts = user_data['edge_owner_to_timeline_media']['edges']
                        posts = [post['node'] for post in posts]

                        for post in posts:
                            utc_datetime = datetime.datetime.fromtimestamp(post['taken_at_timestamp'],
                                                                           tz=datetime.timezone.utc)
                            formatted_date = utc_datetime.strftime('%a %b %d %H:%M:%S %z %Y')
                            try:
                                caption = post['edge_media_to_caption']['edges'][0]['node']['text']
                            except Exception as e:
                                caption = ''
                            if caption == '':
                                caption = None
                            post['post_type'] = 'reels' if post['is_video'] else 'post'
                            post['posted_at'] = formatted_date
                            post['caption'] = caption
                            shortcode = post['shortcode']
                            if post['is_video']:
                                url = f'https://www.instagram.com/reel/{shortcode}'
                            else:
                                url = f'https://www.instagram.com/p/{shortcode}'
                            post['post_url'] = url
                            try:
                                post['likes_count'] = post['edge_liked_by']['count']
                            except Exception as e:
                                post['likes_count'] = post['edge_media_preview_like']['count']
                            post['comments_count'] = post['edge_media_to_comment']['count']
                            post['post_id'] = post['id']
                            data['posts'].append(post)
                        return response
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

