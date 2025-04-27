import requests
import json
import base64
import webbrowser
import os
from urllib.parse import urlparse, parse_qs
from datetime import timedelta

REGION = "eu"  # change to your region ("na", "eu", "ap", "kr") im not sure abt any others

def get_client_version():
    res = requests.get("https://valorant-api.com/v1/version")
    res.raise_for_status()
    return res.json()["data"]["riotClientVersion"]

def get_entitlements_token(token):
    res = requests.post(
        "https://entitlements.auth.riotgames.com/api/token/v1",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={}
    )
    res.raise_for_status()
    return res.json()["entitlements_token"]

def get_puuid(token):
    res = requests.post(
        "https://auth.riotgames.com/userinfo",
        headers={"Authorization": f"Bearer {token}"}
    )
    res.raise_for_status()
    return res.json()["sub"]

def get_platform_encoded():
    plat = {
        "platformType": "PC",
        "platformOS": "Windows",
        "platformOSVersion": "10.0.19042.1.256.64bit",
        "platformChipset": "Unknown"
    }
    raw = json.dumps(plat).encode()
    return base64.b64encode(raw).decode()

def get_storefront(token, ent, puuid, cv):
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Riot-Entitlements-JWT": ent,
        "X-Riot-ClientVersion": cv,
        "X-Riot-ClientPlatform": get_platform_encoded()
    }
    url = f"https://pd.{REGION}.a.pvp.net/store/v3/storefront/{puuid}"
    res = requests.post(url, headers=headers, json={})
    res.raise_for_status()
    return res.json()

def get_wallet(token, ent, puuid, cv):
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Riot-Entitlements-JWT": ent,
        "X-Riot-ClientVersion": cv,
        "X-Riot-ClientPlatform": get_platform_encoded()
    }
    url = f"https://pd.{REGION}.a.pvp.net/store/v1/wallet/{puuid}"
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json()

def get_skin_data(skin_id):
    res = requests.get(f"https://valorant-api.com/v1/weapons/skinlevels/{skin_id}")
    if res.status_code == 200:
        data = res.json()["data"]
        return data["displayName"], data["displayIcon"]
    return "Unknown", ""

def generate_html(skins, reset, vp):
    html = f"""
<html>
<head><title>Valorant Store</title></head>
<body style="font-family:Arial;background:#0f1923;color:#fff;text-align:center;">
  <h1>Daily Store</h1>
  <p><strong>Your VP:</strong> {vp}</p>
  <p><strong>Resets in:</strong> {reset}</p>
  <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:20px;">
"""
    for name, icon in skins:
        html += f"""
    <div style="background:#1f2a38;border-radius:10px;padding:10px;width:200px;">
      <img src="{icon}" alt="{name}" style="width:100%;border-radius:10px;"/>
      <p>{name}</p>
    </div>
"""
    html += """
  </div>
</body>
</html>
"""
    path = os.path.abspath("valorant_store.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open(f"file://{path}")

def extract_tokens(url):
    frag = urlparse(url).fragment
    return parse_qs(frag).get("access_token", [None])[0]

def main():
    webbrowser.open(
        "https://auth.riotgames.com/authorize?"
        "client_id=play-valorant-web-prod&nonce=1"
        "&redirect_uri=https://playvalorant.com/opt_in"
        "&response_type=token%20id_token&scope=account%20openid"
    )
    redirect_url = input("Paste the URL: ").strip()
    token = extract_tokens(redirect_url)
    client_version = get_client_version()
    entitlements = get_entitlements_token(token)
    puuid = get_puuid(token)
    store_data = get_storefront(token, entitlements, puuid, client_version)
    offers = store_data["SkinsPanelLayout"]["SingleItemOffers"]
    reset_seconds = int(store_data["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"])
    reset_time = str(timedelta(seconds=reset_seconds))
    skins = []
    for skin_id in offers:
        name, icon = get_skin_data(skin_id)
        skins.append((name, icon))
    wallet_data = get_wallet(token, entitlements, puuid, client_version)
    vp = wallet_data.get("Balances", {}).get("85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741", 0)
    generate_html(skins, reset_time, vp)

if __name__ == "__main__":
    main()
