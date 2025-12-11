from flask import Flask, jsonify, request, send_from_directory
import os
import requests
import random
import string

app = Flask(__name__, static_folder="public", static_url_path="")

# Environment variables
SITE_NAME = os.getenv("SITE_NAME", "Vinija Checkout Demo")
SITE_URL = os.getenv("SITE_URL", "http://localhost:3000")

YUNO_SECRET_KEY = os.getenv("YUNO_SECRET_KEY", "DEMO_SECRET_NOT_REQUIRED")
YUNO_API_BASE = os.getenv("YUNO_API_BASE", "https://api.sbx.y.uno/v1/payments")


@app.route("/")
def index():
    return send_from_directory("public", "index.html")


@app.route("/config")
def config():
    """Frontend fetches page metadata from here."""
    return jsonify(
        ok=True,
        site_name=SITE_NAME,
        site_url=SITE_URL
    )


def generate_mock_payment(payload):
    payment_id = "pay_" + ''.join(random.choices(string.hexdigits.lower(), k=8))
    return {
        "id": payment_id,
        "status": "pending",
        "amount": payload["amount"],
        "currency": payload["currency"],
        "description": payload["description"]
    }


@app.route("/create-payment", methods=["POST"])
def create_payment():
    payload = request.json

    # Attempt real Yuno call (will fail on your network → fallback)
    try:
        headers = {"Authorization": f"Bearer {YUNO_SECRET_KEY}"}
        r = requests.post(YUNO_API_BASE, json=payload, headers=headers, timeout=8)

        if r.ok:
            return jsonify(ok=True, payment=r.json()), 200
        else:
            raise Exception("Non-200 from Yuno")

    except Exception as e:
        mock = generate_mock_payment(payload)
        return jsonify(
            ok=True,
            payment=mock,
            used_mock=True,
            note="Yuno was unreachable; mock payment returned.",
            error=str(e)
        ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
