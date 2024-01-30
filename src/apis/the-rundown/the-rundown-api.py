import requests

url = "https://therundown-therundown-v1.p.rapidapi.com/sports"

headers = {
	"X-RapidAPI-Key": "SIGN-UP-FOR-KEY",
	"X-RapidAPI-Host": "therundown-therundown-v1.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

print(response.json())