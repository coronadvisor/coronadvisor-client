from flask import Flask
from flask import render_template, request, redirect, url_for
from countryinfo import CountryInfo
from twilio.rest import Client
from cfg import TWILLIO_SID, TWILLIO_TOKEN, TWILLIO_PHONE_NUMBER, TWILLIO_WHITELISTED_NUMBER


import json
import country_converter as coco
import datetime
import re
import csv

app = Flask(__name__)

client = Client(TWILLIO_SID, TWILLIO_TOKEN)


@app.route('/video-demo')
def video_demo():
    return redirect("http://google.com")


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

    d = datetime.datetime.strptime(request.args['date'], "%m/%d/%Y")
    dend = d + datetime.timedelta(days=1)
    display_date = d.strftime('%d %B %Y')
    query_date_start = d.strftime('%Y-%m-%d')
    query_date_end = dend.strftime('%Y-%m-%d')
    query_local_date = d.strftime('%-m/%-d/%Y')
    print(query_date_start)
    print(query_date_end)
    print(query_local_date)

    display_location = city + ", " + country

    locCDCThreat = 0
    neighborCDCThreat = 0

    locPredicted = 0
    dangerScore = 0
    dangerous = False

    valueLocThreatLevel = 0
    threatNeighbors = []

    with open("cdc-data.json") as file:
        data = json.load(file)
        if iso3_country in data.keys() and data[iso3_country] > 1:
            locCDCThreat = 1
            valueLocThreatLevel = data[iso3_country]

        # get neighbors in threat list
        threatNeighbors = {k: v
                           for k, v in data.items() if k in neighbors and data[k] > 1}

        if len(threatNeighbors) > 0:
            print(threatNeighbors)
            neighborCDCThreat = 1

    for k in threatNeighbors.keys():
        threatNeighbors[coco.convert(
            names=k, to="name_short")] = threatNeighbors.pop(k)

    print(threatNeighbors)
    valueThreatNeighbors = ""

    for k in threatNeighbors.keys():
        valueThreatNeighbors += k + " - Level " + str(threatNeighbors[k])

    confirmedCaseCount = 0

    with open("data.csv") as file:
        reader = csv.reader(file, delimiter=",")
        next(reader)

        for row in reader:
            if row[9] == query_local_date and row[10].lower() == country.lower():
                confirmedCaseCount = row[4]

    print(confirmedCaseCount)

    if int(confirmedCaseCount) > 25:
        locPredicted = 1

    params = [locCDCThreat, neighborCDCThreat, locPredicted]
    if params[0] == 1:
        dangerScore += 999999

    if params[1] == 1:
        dangerScore += 1

    if params[2] == 1:
        dangerScore += 1

    if dangerScore >= 2:
        dangerous = True

    return render_template('trip.html', confirmedCaseCount=confirmedCaseCount, query_date_start=query_date_start, query_date_end=query_date_end, valueLocThreatLevel=valueLocThreatLevel, valueThreatNeighbors=valueThreatNeighbors, locCDCThreat=locCDCThreat, params=params, dangerous=dangerous, display_location=display_location, display_date=display_date, phoneValid=phoneValid)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
