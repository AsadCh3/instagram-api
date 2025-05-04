POST_API = "https://www.instagram.com/graphql/query"
PAYLOAD = 'fb_api_caller_class=RelayModern&fb_api_req_friendly_name=PolarisPostActionLoadPostQueryQuery&variables=%7B%22shortcode%22%3A%22{}%22%2C%22fetch_tagged_user_count%22%3Anull%2C%22hoisted_comment_id%22%3Anull%2C%22hoisted_reply_id%22%3Anull%7D&server_timestamps=true&doc_id=8845758582119845'

USER_API = 'https://www.instagram.com/api/v1/users/web_profile_info/?username={}'
# USER_API = 'https://www.instagram.com/{}/?__a=1'
USER_HEADERS = {"User-Agent": "Mozilla/5.0 (Linux; Android 14; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36 Instagram 313.0.0.26.328 Android (34/14; 378dpi; 1080x2215; Google/google; Pixel 6; oriole; oriole; de_DE; 554218055)"}
DEFAULT_HEADERS = {
  'accept': '*/*',
  'accept-language': 'en-US,en;q=0.9',
  'content-type': 'application/x-www-form-urlencoded',
  'origin': 'https://www.instagram.com',
  'priority': 'u=1, i',
  'referer': 'https://www.instagram.com',
  'sec-ch-prefers-color-scheme': 'dark',
  'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
  'sec-ch-ua-full-version-list': '"Chromium";v="134.0.6998.118", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.118"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-model': '""',
  'sec-ch-ua-platform': '"Windows"',
  'sec-ch-ua-platform-version': '"15.0.0"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}
