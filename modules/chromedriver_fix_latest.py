import json
import requests
from webdriver_manager.chrome import ChromeDriverManager 

# Abandoned as of 2023 08 28

url = "https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build.json"
response = requests.get(url)
response_dict = json.loads(response.text)

print(response_dict)

determined_browser_version = response_dict.get("builds").get(determined_browser_version).get("version")

