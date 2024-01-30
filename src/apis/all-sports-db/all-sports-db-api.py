import requests

url = "https://allsportdb-com.p.rapidapi.com/calendar"

querystring = {"objectType":"0"}

headers = {
	"X-RapidAPI-Key": "SIGN-UP-FOR-KEY",
	"X-RapidAPI-Host": "allsportdb-com.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())