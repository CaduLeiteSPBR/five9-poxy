from flask import Flask, request, jsonify
from flask_cors import CORS  # ⬅ importa o módulo CORS
import requests
from base64 import b64encode

app = Flask(__name__)
CORS(app)  # ⬅ habilita CORS para todas as rotas


FIVE9_USER = "cleite@blueruby.info"
FIVE9_PASS = "B0n1f@c100425"
FIVE9_SOAP_URL = "https://api.five9.com/wsadmin/v15/AdminWebService"

SOAP_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ws="http://service.admin.ws.five9.com/">
  <soapenv:Header/>
  <soapenv:Body>
    <ws:getContactRecords>
      <lookupCriteria>
        <contactIdField>number1</contactIdField>
        <criteria>
          <field>number1</field>
          <value>{number}</value>
        </criteria>
      </lookupCriteria>
    </ws:getContactRecords>
  </soapenv:Body>
</soapenv:Envelope>
"""



@app.route("/status", methods=["GET"])
def status():
    number = request.args.get("number")
    headers = {
        "Content-Type": "text/xml;charset=UTF-8",
        "SOAPAction": "",
        "Authorization": "Basic " + b64encode(f"{FIVE9_USER}:{FIVE9_PASS}".encode()).decode()
    }
    payload = SOAP_TEMPLATE.format(number=number)
    response = requests.post(FIVE9_SOAP_URL, headers=headers, data=payload)
    return response.text, response.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
