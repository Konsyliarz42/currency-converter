import requests, csv
from flask import Flask, request, redirect, render_template

#----------------------------------------------------------------
def create_csv():
    response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
    data = response.json()
    data = data[0]['rates']

    with open('rates.csv', 'w', newline='') as csvfile:
        fieldnames  = ['currency', 'code', 'bid', 'ask']
        writer      = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter =';')
        writer.writeheader()

        for x in data:
            writer.writerow(x)

#----------------------------------------------------------------
def convert_to(currency, value):
    with open('rates.csv', newline='') as csvfile:
        reader  = csv.DictReader(csvfile, delimiter =';')
        result = [[line['bid'], line['ask']] for line in reader if line['code'] == currency]
        result = result[0]

    result[0] = round(float(result[0]), 2)
    result[1] = round(float(result[1]), 2)
        
    return result

#================================================================
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def calculate():
    currency    = request.form.get("currency")
    value       = request.form.get("value")

    if currency and value:
        result  = convert_to(currency, value)
        bid     = str(result[0])
        ask     = str(result[1])
        print(currency, value, bid, ask)
        
    else:
        bid = '-'

    if request.method == 'GET':
        return render_template("calculator.html")

    elif request.method == 'POST':
        return render_template("calculator.html", bid=bid, ask=ask, currency=currency, value=value)
