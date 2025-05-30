import requests
import json
from box import Box
from datetime import datetime


def each_post_details(
    short_code="",
):
    try:
        variables = {
            "shortcode": short_code,
            "fetch_comment_count": "40",
            "parent_comment_count": "24",
            "child_comment_count": "3",
            "fetch_like_count": "10",
            "fetch_tagged_user_count": "null",
            "fetch_preview_comment_count": "2",
            "has_threaded_comments": "true",
            "hoisted_comment_id": "null",
            "hoisted_reply_id": "null",
        }
        proxy = {
            "http": "http://uikycltr-rotate:umoozz54hauf@p.webshare.io:80",
            "https": "http://uikycltr-rotate:umoozz54hauf@p.webshare.io:80",
        }
        data = {
            "av": "0",
            "__d": "www",
            "__user": "0",
            "__a": "1",
            "__req": "3",
            "__hs": "19830.HYP:instagram_web_pkg.2.1..0.0",
            "dpr": "1",
            "__ccg": "UNKNOWN",
            "__rev": "1012841957",
            "__comet_req": "7",
            "lsd": "AVq7-e0F3Wk",
            "jazoest": "2828",
            "__spin_r": "1012841957",
            "__spin_b": "trunk",
            "__spin_t": "1713368437",
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "PolarisPostActionLoadPostQueryQuery",
            "variables": json.dumps(variables),
            "server_timestamps": "true",
            "doc_id": "24852649951017035",
        }
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "dpr": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "pragma": "no-cache",
            "x-asbd-id": "129477",
            "x-csrftoken": "uJ2xECzzB4GkWgi07L1jnLiKVmYx9jnj",
            "x-ig-app-id": "1217981644879628",
            "x-ig-www-claim": "hmac.AR1t1n8du_vvy2J2eTLt8lsrLyWQiH6MHpzm41GMZriV5yoT",
            "x-requested-with": "XMLHttpRequest",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }

        # encoded_data = urlencode(data)
        response = requests.post(
            "https://www.instagram.com/graphql/query",
            data=data,
            headers=headers,
            proxies=proxy,
        )
        print("Status Code:", response.status_code)
        # print("Headers:", response.headers)
        # print("Response Body:", response.text)  # Log the full body of the response
        allPost = json.loads(response.text)
        allPost = Box(allPost)
        data = allPost.data.xdt_shortcode_media
        # if data is None:
        #     print(f"No detail data available")

        video_url = data.get("video_url", None) if data else None
        # else:
        #     None
        post_id = data.get("id", None) if data else None
        video_view_count = data.get("video_view_count", None) if data else None
        video_play_count = data.get("video_play_count", None) if data else None
        video_duration = data.get("video_duration", None) if data else None

        post_date_ts = data.get("taken_at_timestamp", "") if data else ""
        post_date = datetime.fromtimestamp(int(post_date_ts))
        latest_comments = []
        comments_edges = (
            data.get("edge_media_to_parent_comment", {}).get("edges", [])
            if data
            else None
        )
        if comments_edges:
            for edge in comments_edges:
                node = edge["node"]
                id = node["id"]
                ownerUserName = node["owner"]["username"]
                text = node["text"]
                created_at = node["created_at"]
                likes_count = node["edge_liked_by"]["count"]
                owner_profile_pic = node["owner"]["profile_pic_url"]
                latest_comments.append(
                    {
                        "id": id,
                        "ownerUserName": ownerUserName,
                        "text": text,
                        "likes_count": likes_count,
                        "created_at": created_at,
                        "owner_profile_pic": owner_profile_pic,
                    }
                )

        # print(latest_comments)
        sponsor_users = []
        sponsor_data = (
            data.get("edge_media_to_sponsor_user").get("edges", []) if data else None
        )
        if sponsor_data:
            for user in sponsor_data:
                sponsor_users.append(user)
        print("sponsor__user ====>>", sponsor_users)
        owner = data.owner if data else None
        is_affiliate = data.is_affiliate if data else None
        is_paid_partnership = data.is_paid_partnership if data else None
        is_ad = data.is_ad if data else None

        results_box = Box(
            {
                "post_id": post_id,
                "short_code": short_code,
                "video_url": video_url,
                "video_view_count": video_view_count,
                "video_play_count": video_play_count,
                "video_duration": video_duration,
                "post_date": post_date,
                "sponsor_user": sponsor_users,
                "owner": owner,
                "is_affiliate": is_affiliate,
                "is_paid_partnership": is_paid_partnership,
                "is_ad": is_ad,
                "latest_comments": latest_comments
            }
        )
        results = results_box.to_dict()

        print(results)
    except Exception as e:
        print(e)


print(each_post_details(short_code="DJQ2W1STnUP"))