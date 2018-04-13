# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import requests
#import configparser

from chatbase import Message, MessageSet, MessageTypes, InvalidMessageTypeError
from sheetsu import SheetsuClient
from datetime import datetime, time
#import gspread
#from oauth2client.service_account import ServiceAccountCredentials

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

#appel des API
def processRequest(req):
    #météo
    if req.get("result").get("action")=="yahooWeatherForecast":
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = makeYqlQuery(req)
        if yql_query is None:
           return {}
        yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json&lang=fr-FR"
        result = urlopen(yql_url).read()
        data = json.loads(result)
        res = makeWebhookResult(data)
    elif req.get("lang")=="fr":
        result = req.get("result")
        message_user = result.get("resolvedQuery")
        metadata = result.get("metadata")
        intent = metadata.get("intentName")
        timestamp = req.get("timestamp")
        user_id = req.get("id")
        platform = 'Dialogflow'
        api_key = '56bd0b2b-4b67-4522-8933-1ff443a8a922'
        
          # Create an instance of MessageSet to collect all the messages
        #message_set = MessageSet(api_key=api_key, platform=platform,
             #version=version, user_id=user_id)
          # Create an instance of Message for the user message and set values in the constructor
        #msg1 = Message(api_key=api_key, platform=platform, message=message,
            #intent=intent, version=version, user_id=user_id,
            #type=MessageTypes.USER, not_handled=True,
            #time_stamp=time_stamp)
          # Set the message as "handled" because the NLP was able to successfully decode the intent
        #msg1.set_as_feedback()

          # Create an instance of Message for the bot response message and set values in the constructor
        #msg2 = Message(api_key=api_key, platform=platform, message=message,
            #version=version, user_id=user_id,
            #type=MessageTypes.AGENT)
        #message_set = MessageSet(api_key=api_key, platform=platform,
                         version=version, user_id=user_id)

          # Push messages into the collection (MessageSet)
        #message_set.append_message(msg1)
        #message_set.append_message(msg2)

          # Send the messages
        #response = message_set.send()
          # response.status_code will be 200 if sending worked
    #météoopen
    elif req.get("result").get("action")=="openweather":
        baseurl = "api.openweathermap.org/data/2.5/weather?"
        owm_query = makeOwmQuery(req)
        #if owm_query is None:
           #return {}
        owm_url = baseurl + urlencode({'q': owm_query}) + "&lang=fr&APPID=8436a2c87fc4408d01d9f7f92e9759ca"
        result = urlopen(owm_url).read()
        data = json.loads(result)
        res = makeWebhookResultopen(data)
    #sheet exposant
    elif req.get("result").get("action")=="readsheet-exp":
        GsExp_query = makeGsExpQuery(req)
        ChatBasequery(req)
        #chatbaseProcess(message_user, metadata, intent, timestamp, user_id, platform, api_key)
        client = SheetsuClient("https://sheetsu.com/apis/v1.0su/27ac2cb1ff16")
        data = client.search(sheet="Exposant", nom=GsExp_query)
        res = makeWebhookResultForSheetsExp(data)
     #sheet bus
    elif req.get("result").get("action")=="readsheet-bus":
        GsBus_query = makeGsBusQuery(req)
        client = SheetsuClient("https://sheetsu.com/apis/v1.0su/27ac2cb1ff16")
        data = client.search(sheet="Navette", date=GsBus_query)
        res = makeWebhookResultForSheetsBus(data)
     #sheet session
    elif req.get("result").get("action")=="readsheet-ses":
        GsSes_query = makeGsSesQuery(req)
        client = SheetsuClient("https://sheetsu.com/apis/v1.0su/27ac2cb1ff16")
        data = client.search(sheet="Conference", date=GsSes_query) 
        res = makeWebhookResultForSheetsSes(data)
      #sheetnow  
    elif req.get("result").get("action")=="readsheet-ses-now":
        #GsSesNow_query = makeGsSesNowQuery(req)
        client = SheetsuClient("https://sheetsu.com/apis/v1.0su/27ac2cb1ff16")
        data = client.read(sheet="Conference") 
        res = makeWebhookResultForSheetsSesNow(data)
    
    
    else:
        return {}

    return res

#def chatbaseProcess(message_user, metadata, intent, timestamp, user_id, platform, api_key):
    
   #return None
    
    
     
    
    
    
    
#fonction pour créer la query pour exposant
def makeGsExpQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    exp = parameters.get("Exposant")
    if exp is None:
        return None
    return exp

#fonction qui trie les données à afficher pour API googlesheet exposant
def makeWebhookResultForSheetsExp(data):
    nom = data[0]['nom']
    emp = data[0]['emplacement']
    des = data[0]['description']
    speech = nom + " ce trouve à l'emplacement " + emp + ", c'est un " + des
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

def makeGsBusQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    date = parameters.get("date")
    if date is None:
        return None
    return date

#fonction afin d'afficher API googlesheet pour bus
def makeWebhookResultForSheetsBus(data):
    hoa = data[0]['horaire aller']
    hor = data[0]['horaire retour']
    speech = "Le bus a pour horaire aller: " + hoa + " et retour: " + hor
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

#fonction pour prendre le parametre date pour Sheet session
def makeGsSesQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    date = parameters.get("date")
    if date is None:
        return None
    return date

#fonction afin d'afficher API googlesheet pour session
def makeWebhookResultForSheetsSes(data):
    value = []
    for each in data:
        value.append(each['Partner'])
    nom = ', '.join(map(str, value))
    date = data[0]['date']
    speech = "Les partenaires exposant le " + date + " sont: " + nom
    return {
          "speech": speech,
          "displayText": speech,
           #"data": data,
           #"contextOut": [],
          "source": "apiai-weather-webhook-sample"
        }
        

#def makeGsSesNowQuery(req):
    #result = req.get("result")
    #parameters = result.get("parameters")
    #time = parameters.get("time")
    #if time is None:
        #return None
    #return time

#fonction permettant d'afficher les sessions en temps réels à terminer
def makeWebhookResultForSheetsSesNow(data):
    result = req.get("result")
    parameters = result.get("parameters")
    time = parameters.get("time")
    now = datetime.now()
    now_time = now.time()
    #timeStart = data[0]['Start time']
    #timeEnd = data[0]['End time']
    if now_time >= time(10,30) and now_time <= time(16,30):
       speech = "C'est dans l'intervalle"
    else:
       speech = "Ce n'est pas dans l'intervalle"
    #value = []
    #for each in data:
        #value.append(each['Start time'])
    #nom = ', '.join(map(str, value))
    #speech = "Les sessions sont: " + nom
    
    return {
         "speech": speech,
         "displayText": speech,
         # "data": data,
         # "contextOut": [],
         "source": "apiai-weather-webhook-sample"
       }

def makeOwmQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    #if city is None:
        #return None
    return city

def makeWebhookResultopen(data):
    speech = data['weather']
    return {
        "speech": speech,
        "displayText": speech,
         #"data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

#fonction création de la query pour API météo
def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "') and u='c'"

#fonction qui trie les données à afficher pour API météo
def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "La météo à " + location.get('city') + ": " + "La température est de " + condition.get('temp') + " " + units.get('temperature')
    #+ condition.get('text') + \

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
