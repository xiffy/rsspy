import time
import requests

print("|+-+ Digesting @ %s +-+-+-+-+-+-+-+|" % time.strftime("%c"))

r = requests.get("https://rss.xiffy.nl/send_digest")
