from flask import Flask, request
from collections import defaultdict
import time

app = Flask(__name__)
recent_swaps = defaultdict(list)

@app.route('/webhook', methods=['POST'])
def handle_helius():
    data = request.json
    transactions = data.get("transactions", [])
    now = time.time()

    for tx in transactions:
        swap_event = tx.get("events", {}).get("swap")
        if not swap_event:
            continue

        wallet = tx["description"].split()[0]  # crude wallet guess
        token_out = swap_event.get("tokenTo", {}).get("mint")

        if not wallet or not token_out:
            continue

        recent_swaps[token_out] = [
            (w, t) for (w, t) in recent_swaps[token_out] if now - t < 300
        ] + [(wallet, now)]

        unique_wallets = set(w for w, _ in recent_swaps[token_out])
        if len(unique_wallets) >= 2:
            print(f"🔔 ALERT: {len(unique_wallets)} wallets bought {token_out}")

    return "ok", 200
