import requests

url = "https://sportspage-feeds.p.rapidapi.com/rankings"

querystring = {"league":"NCAAF"}

headers = {
	"X-RapidAPI-Key": "SIGN-UP-FOR-KEY",
	"X-RapidAPI-Host": "sportspage-feeds.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())