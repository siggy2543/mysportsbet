from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import apis.request.requests as requests 

def get_title(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return None
    try:
        soup = BeautifulSoup(response.read(), 'html.parser')
        titles = soup.find_all('h1')
        if len(titles) > 0:
            return [title.get_text() for title in titles]
        else:
            return None
    except AttributeError as e:
        return None

titles = get_title('https://www.espn.com/')
titles2 = get_title('https://espnbet.com/')

if titles is None:
    print('Title could not be found')
else:
    for title in titles:
        print(title)
        
nameList = bs.findAll('script', {'script data-partytown':'{text}'}) # Replace script with appropriate tags
nameList = bs.findAll(id='text', class_='text') # Replace id and class with relevent ones
nameList = bs.findAll('', {'id':'text'}) # This line is same as above one, choose what you like better

for name in nameList:
    print(name.get_text())