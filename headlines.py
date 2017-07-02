from flask import Flask
import feedparser
from flask import render_template
from flask import request
import json
import urllib
import config

app = Flask(__name__)

DEFAULTS =  {'publication': 'bbc', 
'city': 'Los Angeles, US',
'currency_from': 'USD',
'currency_to': 'INR'}
WEATHER_URL =  "http://api.openweathermap.org/data/2.5/weather?q={} &units=metric&APPID=" + config.weather_api_key
CURRENCY_URL =  "https://openexchangerates.org//api/latest.json?app_id="+ config.currency_api_key

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
'cnn': 'http://rss.cnn.com/rss/edition.rss',
'fox': 'http://feeds.foxnews.com/foxnews/latest',
'iol': 'http://www.iol.co.za/cmlink/1.640',
'aspnet':'https://www.asp.net/rss/dailyarticles'}


@app.route("/")
def home():
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)

    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)

    currency_from = request.args.get('currency_from')
    if not currency_from:
        currency_from = DEFAULTS['currency_from']
    currency_to = request.args.get('currency_to')
    if not currency_to:
        currency_to = DEFAULTS['currency_to']

    rate,currencies = get_rate(currency_from, currency_to)

    return render_template('home.html', 
    articles=articles,weather=weather,
    currency_from=currency_from, currency_to=currency_to,rate=rate,
    currencies=sorted(currencies))

def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']
    

def get_weather(query):
    query = urllib.parse.quote(query)
    url =WEATHER_URL.format(query)
    data = urllib.request.urlopen(url).read()
    str_data = data.decode('utf-8')
    parsed = json.loads(str_data)
    weather = None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"],
        "temperature":parsed["main"]["temp"],
        "city":parsed["name"],
        'country':parsed['sys']['country']}
    return weather

def get_rate(frm, to):
    all_currency = urllib.request.urlopen(CURRENCY_URL).read().decode('utf-8')

    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate/frm_rate, parsed.keys())

if __name__ == '__main__':
    app.run(port=5000, debug=True)