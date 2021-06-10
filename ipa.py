from bs4 import BeautifulSoup
import requests

HELP_URL = r"https://help.keyman.com/keyboard/sil_ipa/1.8.5/sil_ipa"
OUTFILE = "ipa.compose"

print(BeautifulSoup(requests.get(HELP_URL).text, "lxml"))
