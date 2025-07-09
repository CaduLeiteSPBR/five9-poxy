from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from base64 import b64encode
import xml.etree.ElementTree as ET
import os
import re

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
    if not number:
        return jsonify({"error": "Número não informado"}), 400

    headers = {
        "Content-Type": "text/xml;charset=UTF-8",
        "SOAPAction": "",
        "Authorization": "Basic " + b64encode(f"{FIVE9_USER}:{FIVE9_PASS}".encode()).decode()
    }

    payload = SOAP_TEMPLATE.format(number=number)
    response = requests.post(FIVE9_SOAP_URL, headers=headers, data=payload)

    try:
        root = ET.fromstring(response.text)
        ns = {"env": "http://schemas.xmlsoap.org/soap/envelope/"}

        body = root.find("env:Body", ns)
        if body is None:
            return jsonify({"error": "Sem body na resposta"}), 500

        # Extrai todos os campos e valores
        field_names = [f.text.strip() for f in body.findall(".//fields")]
        data_values = [d.text.strip() if d.text else "" for d in body.findall(".//records/values/data")]

        result = dict(zip(
            [re.sub(r'\W+', '_', name.lower()) for name in field_names],
            data_values
        ))

        return jsonify({
            "last_disposition": result.get("last_disposition", ""),
            "message": result.get("message", ""),
            "debug": result  # opcional: remover depois
        })

    except ET.ParseError:
        return jsonify({"error": "Erro ao analisar XML da resposta da Five9"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
