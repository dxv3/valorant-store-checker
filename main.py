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
    return res.json()['data']['riotClientVersion']

def get_entitlements_token(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(
        'https://entitlements.auth.riotgames.com/api/token/v1',
        headers=headers,
        json={}
    )
    return response.json()['entitlements_token']

def get_puuid(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.post('https://auth.riotgames.com/userinfo', headers=headers)
    return response.json()['sub']

def get_storefront(access_token, entitlements_token, puuid, client_version):
    platform_json = {
        "platformType": "PC",
        "platformOS": "Windows",
        "platformOSVersion": "10.0.19042.1.256.64bit",
        "platformChipset": "Unknown"
    }
    encoded_platform = base64.b64encode(json.dumps(platform_json).encode()).decode()

    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Riot-Entitlements-JWT': entitlements_token,
        'X-Riot-ClientVersion': client_version,
        'X-Riot-ClientPlatform': encoded_platform
    }

    url = f"https://pd.{REGION}.a.pvp.net/store/v3/storefront/{puuid}"
    
    response = requests.post(url, headers=headers, json={})
    
    return response.json()



def get_skin_data(skin_id):
    res = requests.get(f"https://valorant-api.com/v1/weapons/skinlevels/{skin_id}")
    if res.status_code == 200:
        data = res.json()["data"]
        return data["displayName"], data["displayIcon"]
    return "Unknown", ""

def generate_html(skin_data, reset_time):
    html = f"""
    <html>
    <head><title>Valorant Store</title></head>
    <body style='font-family: Arial; background-color: #0f1923; color: white; text-align: center;'>
    <h1>Daily Store</h1>
    <p>Resets in: {reset_time}</p>
    <div style='display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;'>
    """
    for name, icon in skin_data:
        html += f"""
        <div style='background: #1f2a38; padding: 10px; border-radius: 10px; width: 200px;'>
            <img src='{icon}' alt='{name}' style='width: 100%; border-radius: 10px;'>
            <p>{name}</p>
        </div>
        """
    html += "</div></body></html>"
    with open("valorant_store.html", "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open(f"file://{os.path.abspath('valorant_store.html')}")

def extract_tokens(url):
    fragment = urlparse(url).fragment
    params = parse_qs(fragment)
    return {
        "access_token": params.get("access_token", [None])[0],
        "id_token": params.get("id_token", [None])[0]
    }

def main():
    print("🔓 Opening Riot login page...")
    webbrowser.open(
        "https://auth.riotgames.com/authorize?client_id=play-valorant-web-prod"
        "&nonce=1&redirect_uri=https://playvalorant.com/opt_in"
        "&response_type=token%20id_token&scope=account%20openid"
    )
    redirect_url = input("Paste redirect URL here: ").strip()
    tokens = extract_tokens(redirect_url)
    access_token = tokens["access_token"]
    id_token = tokens["id_token"]
    client_version = get_client_version()
    entitlements_token = get_entitlements_token(access_token)
    puuid = get_puuid(access_token)

    try:
        store_data = get_storefront(access_token, entitlements_token, puuid, client_version)
        offers = store_data["SkinsPanelLayout"]["SingleItemOffers"]
        duration = int(store_data["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"])
        readable_time = str(timedelta(seconds=duration))
        skins = [get_skin_data(skin) for skin in offers]
        generate_html(skins, readable_time)
    except Exception as e:
        print("Failed to load store:", e)

if __name__ == "__main__":
    main()