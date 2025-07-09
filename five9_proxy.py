from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from base64 import b64encode
import xml.etree.ElementTree as ET
import os
import re

app = Flask(__name__)
CORS(app)

# Credenciais da API Five9
FIVE9_USER = "cleite@blueruby.info"
FIVE9_PASS = "B0n1f@c100425"
FIVE9_SOAP_URL = "https://api.five9.com/wsadmin/v15/AdminWebService"

# Template SOAP para getContactRecords
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
    if not number:
        return jsonify({"error": "Número não informado"}), 400

    headers = {
        "Content-Type": "text/xml;charset=UTF-8",
        "SOAPAction": "",
        "Authorization": "Basic " + b64encode(f"{FIVE9_USER}:{FIVE9_PASS}".encode()).decode()
    }

    payload = SOAP_TEMPLATE.format(number=number)
    response = requests.post(FIVE9_SOAP_URL, headers=headers, data=payload)

    print("📥 XML recebido da Five9:\n", response.text[:3000])  # loga os primeiros 3000 caracteres

    return response.text, 200, {"Content-Type": "text/xml"}



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
