from flask import Flask
from flask import render_template, request, redirect, url_for
from countryinfo import CountryInfo
from twilio.rest import Client
from cfg import TWILLIO_SID, TWILLIO_TOKEN, TWILLIO_PHONE_NUMBER, TWILLIO_WHITELISTED_NUMBER

import geocoder
import json
import country_converter as coco
import datetime
import re

app = Flask(__name__)

client = Client(TWILLIO_SID, TWILLIO_TOKEN)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sms', methods=['POST'])
def sms():
    phone = "+1" + re.sub('[^0-9]', '', request.form['phone']).strip()

    if phone != TWILLIO_WHITELISTED_NUMBER:
        return redirect(request.referrer + "&phone=invalid")

    client.messages.create(
        to=phone,
        from_=TWILLIO_PHONE_NUMBER,
        body="""


        You have been signed up to receive notifications about your travel destination.
        Location: {0}
        Date: {1}
        
        
        """.format(request.form['display_location'], request.form['display_date']))
    return redirect(request.referrer + "&phone=valid")


@app.route('/trip', methods=['GET'])
def trip():
    if (request.args['location'] == '' or request.args['date'] == ''):
        return redirect(url_for('index'))

    phoneValid = "none"
    print(request.args)

    if 'phone' in request.args:
        if request.args['phone'] == "valid":
            phoneValid = "true"
        else:
            phoneValid = "false"

    country = coco.convert(names=[request.args['location'].split(
        ',')[-1].strip()], to="name_short")
    iso3_country = coco.convert(names=[request.args['location'].split(
        ',')[-1].strip()], to="ISO3")
    city = request.args['location'].split(',')[0].strip()

    cinfo = CountryInfo(country)
    neighbors = cinfo.borders()
    iso3_neighbors = coco.convert(names=neighbors, to="ISO3")

    d = datetime.datetime.strptime(request.args['date'], "%m/%d/%Y")
    display_date = d.strftime('%d %B %Y')
    display_location = city + ", " + country

    locCDCThreat = 0
    neighborCDCThreat = 0
    threatNeighbors = []
    locPredicted = 0
    neighborPredicted = 0
    neighborPredictedList = {}
    dangerScore = 0
    dangerous = False

    with open("cdc-data.json") as file:
        data = json.load(file)
        if iso3_country in data.keys():
            locCDCThreat = 1

        # get neighbors in threat list
        threatNeighbors = [{k: v}
                           for k, v in data.items() if k in neighbors]

        if len(threatNeighbors) > 0:
            print(threatNeighbors)
            neighborCDCThreat = 1

    g = geocoder.google(request.args['location'])
    locPredicted = 1
    neighborPredicted = 1
    params = [locCDCThreat, neighborCDCThreat, locPredicted, neighborPredicted]
    if params[0] == 1:
        dangerScore += 999999

    if params[1] == 1:
        dangerScore += 1

    if params[2] == 1:
        dangerScore += 1

    if params[3] == 1:
        dangerScore += 1

    if dangerScore >= 3:
        dangerous = True

    return render_template('trip.html', params=params, dangerous=dangerous, display_location=display_location, display_date=display_date, phoneValid=phoneValid)
