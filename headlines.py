from flask import Flask
import feedparser
from flask import render_template
from flask import request
import json
import urllib
import config
import datetime
from flask import make_response

app = Flask(__name__)

DEFAULTS =  {'publication': 'bbc', 
'city': 'Los Angeles, US',
'currency_from': 'USD',
'currency_to': 'GBP'}
WEATHER_URL =  "http://api.openweathermap.org/data/2.5/weather?q={} &units=imperial&APPID=" + config.weather_api_key
CURRENCY_URL =  "https://openexchangerates.org//api/latest.json?app_id="+ config.currency_api_key

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
'cnn': 'http://rss.cnn.com/rss/edition.rss',
'fox': 'http://feeds.foxnews.com/foxnews/latest',
'iol': 'http://www.iol.co.za/cmlink/1.640',
'google':'https://news.google.com/news/rss/?ned=us&hl=en',
'aspnet':'https://www.asp.net/rss/dailyarticles'}


@app.route("/")
def home():
    publication = get_value_with_fallback('publication')
    articles = get_news(publication)

    city = get_value_with_fallback("city")
    weather = get_weather(city)

    currency_from = get_value_with_fallback('currency_from')
    
    currency_to = get_value_with_fallback('currency_to')
   
    rate,currencies = get_rate(currency_from, currency_to)

    

    response = make_response( render_template('home.html', 
    articles=articles,weather=weather,publication=publication,
    currency_from=currency_from, currency_to=currency_to,rate=rate,
    currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response

def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]
    
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