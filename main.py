import requests
import base64
import json
import socket
import time
import os
from concurrent.futures import ThreadPoolExecutor

SOURCES = [
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/mahdicold/V2Ray-Config-Sub/main/v2ray-config.txt",
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/w1770946466/Auto_Proxy/main/Long_term_subscription_num"
]

def get_country(host):
    try:
        ip = socket.gethostbyname(host)
        res = requests.get(f"http://ip-api.com/json/{ip}?fields=countryCode", timeout=3).json()
        return res.get('countryCode', 'UN')
    except:
        return "UN"

def check_connection(host, port):
    try:
        start_time = time.time()
        sock = socket.create_connection((host, port), timeout=2)
        latency = int((time.time() - start_time) * 1000)
        sock.close()
        return latency
    except:
        return None

def extract_info(config):
    try:
        if config.startswith("vmess://"):
            data = json.loads(base64.b64decode(config[8:]).decode('utf-8'))
            return data.get('add'), int(data.get('port'))
        elif "@" in config:
            parts = config.split("@")[1].split("?")[0].split("#")[0]
            if ":" in parts:
                host, port = parts.split(":")
                return host, int(port)
    except:
        pass
    return None, None

def process_config(conf):
    if not conf.startswith(("vless", "vmess", "trojan", "ss")):
        return None
    host, port = extract_info(conf)
    if host and port:
        latency = check_connection(host, port)
        if latency:
            country = get_country(host)
            return {"conf": conf, "country": country, "latency": latency}
    return None

def main():
    raw_configs = set()
    headers = {"User-Agent": "Mozilla/5.0 (Rpix-Bot)"}
    for url in SOURCES:
        try:
            res = requests.get(url, headers=headers, timeout=15)
            content = res.text
            if "://" not in content[:50]:
                try: content = base64.b64decode(content).decode('utf-8', 'ignore')
                except: pass
            raw_configs.update(content.splitlines())
        except: continue

    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(process_config, list(raw_configs)))
    
    valid_results = sorted([r for r in results if r], key=lambda x: x['latency'])
    final_configs = []
    for i, item in enumerate(valid_results[:100]):
        clean_conf = item['conf'].split("#")[0]
        final_configs.append(f"{clean_conf}#Pix.{item['country']}.{i+1}")

    os.makedirs("export", exist_ok=True)
    with open("export/sub.txt", "w") as f: f.write("\n".join(final_configs))
    with open("export/sub_ios.txt", "w") as f:
        f.write(base64.b64encode("\n".join(final_configs).encode()).decode())

if __name__ == "__main__":
    main()
