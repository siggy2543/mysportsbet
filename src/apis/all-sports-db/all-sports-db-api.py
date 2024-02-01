import apis.request.requests as requests
import os

url = "https://allsportdb-com.p.rapidapi.com/calendar"

querystring = {"objectType":"0"}

headers = {
	"X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
	"X-RapidAPI-Host": "allsportdb-com.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())