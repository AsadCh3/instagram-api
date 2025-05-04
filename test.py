import requests
import time
from concurrent.futures import ThreadPoolExecutor

# Request configuration
url = "http://13.234.21.33:8080/api/users?user_id=business.tamizha&key=J2pQvkrA75KtrVHpKuc41XqLON4pyw2ilO6beOYhJiLxHbnE3V"
headers = {}
payload = {}

# Request parameters
total_requests = 100
requests_per_second = 100


def make_request(request_number):
    start_time = time.time()
    response = requests.request("GET", url, headers=headers, data=payload)
    end_time = time.time()

    print(f"Request {request_number + 1}: Status Code {response.status_code}, Time: {end_time - start_time:.4f}s")
    print(response.json().keys())
    return response.text


# Use ThreadPoolExecutor to make concurrent requests
with ThreadPoolExecutor(max_workers=requests_per_second) as executor:
    for batch in range(0, total_requests, requests_per_second):
        batch_start = time.time()

        # Submit a batch of requests
        futures = []
        for i in range(batch, min(batch + requests_per_second, total_requests)):
            futures.append(executor.submit(make_request, i))

        # Wait for all futures to complete
        for future in futures:
            future.result()

        # Calculate how long to wait before starting the next batch
        batch_duration = time.time() - batch_start
        #if batch_duration < 1.0:
        #time.sleep(1.0 - batch_duration)

        print(f"Completed batch {batch // requests_per_second + 1}/{total_requests // requests_per_second}")

print(f"All {total_requests} requests completed")

