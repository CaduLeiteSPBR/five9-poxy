from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from base64 import b64encode
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)
CORS(app)

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

    root = ET.fromstring(response.text)

    # Busca todos os campos retornados
    namespaces = {"soapenv": "http://schemas.xmlsoap.org/soap/envelope/"}
    body = root.find("soapenv:Body", namespaces)
    record_fields = body.findall(".//field")

    result = {}
    for field in record_fields:
        name_elem = field.find("name")
        value_elem = field.find("value")
        if name_elem is not None and value_elem is not None:
            result[name_elem.text] = value_elem.text

    return jsonify({
        "last_disposition": result.get("last_disposition") or result.get("lastDisposition") or "",
        "message": result.get("message") or ""
    })
