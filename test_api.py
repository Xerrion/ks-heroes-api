"""Quick test to check API response structure."""

import json

import httpx

response = httpx.get("http://127.0.0.1:8000/exclusive-gear/?hero=jabel")
data = response.json()

if data:
    gear = data[0]
    print("=== GEAR KEYS ===")
    print(list(gear.keys()))

    print("\n=== FIRST LEVEL KEYS ===")
    if gear.get("levels"):
        print(list(gear["levels"][0].keys()))

    print("\n=== CONQUEST SKILL KEYS ===")
    if gear.get("conquest_skill"):
        print(list(gear["conquest_skill"].keys()))

    print("\n=== FULL RESPONSE (pretty) ===")
    print(json.dumps(data[0], indent=2))
