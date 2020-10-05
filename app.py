import requests, csv
from flask import Flask, request, redirect, render_template

#----------------------------------------------------------------
def create_csv():
    """This function get data from api and create csv file.
    After this returns list with names currencies."""

    response    = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
    data        = response.json()
    data        = data[0]['rates']
    names       = list()

    with open('rates.csv', 'w', newline='') as csvfile:
        fieldnames  = ['currency', 'code', 'bid', 'ask']
        writer      = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter =';')
        writer.writeheader()

        for x in data:
            writer.writerow(x)
            names.append(x['currency'].capitalize())
            names[-1] += ' (' + x['code'] + ')'
            
    return names

#----------------------------------------------------------------
def convert_to_pln(currency, value):
    """This function check csv for currency and returns purchase price in PLN."""

    with open('rates.csv', newline='') as csvfile:
        reader  = csv.DictReader(csvfile, delimiter =';')
        result  = [line['bid'] for line in reader if line['code'] == currency]

    value       = float(value)
    result[0]   = round(float(result[0])*value, 2)
 
    return result[0]

#----------------------------------------------------------------
def convert_pln_to(currency, value):
    """This function check csv for currency and returns selling price."""
    
    with open('rates.csv', newline='') as csvfile:
        reader  = csv.DictReader(csvfile, delimiter =';')
        result  = [line['ask'] for line in reader if line['code'] == currency]

    value       = float(value)
    result[0]   = round(1/float(result[0])*value, 2)
 
    return result[0]

#================================================================
app     = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def calculate():
    names       = create_csv()
    value       = request.form.get("value")
    currency    = request.form.get("currency")
    convert     = request.form.get('convert')

    if type(value) == str:
        try:
            float(value)
        except ValueError:
            value = False
    
        if currency and value:
            name        = currency[:currency.rfind('(')]
            currency    = currency[currency.rfind('(') + 1:-1]
            cname       = convert[:convert.rfind('(')]
            convert     = convert[convert.rfind('(') + 1:-1]

            if currency != convert:
                if currency == 'PLN':
                    result = convert_pln_to(convert, value)
                else:
                    result = convert_to_pln(currency, value)
            else:
                result = value

        if request.method == 'POST' and value:
            return render_template("calculator.html",   names=names,
                                                        value=value, currency=currency, name=name,
                                                        result=result, convert=convert, cname=cname )

    return render_template("calculator.html", names=names)
