import requests, base64, socket, ssl, random, re, os
from urllib.parse import urlparse, parse_qs, urlencode, unquote, quote
from concurrent.futures import ThreadPoolExecutor

TARGET_COUNT = 50
TIMEOUT = 1.5
EXPORT_DIR = "export"

# لیست منابع و آی‌پی‌های تمیز طبق استاندارد IRPX
SOURCES = [
    "https://raw.githubusercontent.com",
    "https://raw.githubusercontent.com",
    "https://raw.githubusercontent.com"
]
CLEAN_IPS = ["104.16.1.1", "104.17.1.1", "104.18.1.1", "104.19.1.1"]

def decode_base64_if_needed(text):
    try:
        if "://" not in text: return base64.b64decode(text + '=' * (-len(text) % 4)).decode('utf-8')
    except: pass
    return text

def check_connection(target_ip, port, sni):
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with socket.create_connection((target_ip, int(port)), timeout=TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=sni) as ssock: return True
    except: return False

def process_config(conf):
    try:
        conf = unquote(conf).strip()
        parsed = urlparse(conf)
        if parsed.scheme not in ['vless', 'trojan']: return None
        user_info, host_port = parsed.netloc.split("@", 1)
        original_address, port = host_port.rsplit(":", 1) if ":" in host_port else (host_port, "443")
        params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        actual_sni = params.get('sni', params.get('host', original_address))
        clean_ip = random.choice(CLEAN_IPS)
        if check_connection(clean_ip, port, actual_sni):
            params.update({'sni': actual_sni, 'host': actual_sni})
            query_str = urlencode(params)
            remark = quote("🚀_IRPX_Clean")
            return f"{parsed.scheme}://{user_info}@{clean_ip}:{port}?{query_str}#{remark}"
    except: pass
    return None

def main():
    if not os.path.exists(EXPORT_DIR): os.makedirs(EXPORT_DIR)
    all_raw = set()
    for s in SOURCES:
        try:
            res = requests.get(s, timeout=10).text
            all_raw.update(re.findall(r'(?:vless|trojan)://[^\s]+', decode_base64_if_needed(res)))
        except: continue
    raw_list = list(all_raw)
    random.shuffle(raw_list)
    with ThreadPoolExecutor(max_workers=25) as executor:
        results = list(filter(None, executor.map(process_config, raw_list[:600])))
    final_str = "\n".join(results[:TARGET_COUNT])
    b64_content = base64.b64encode(final_str.encode('utf-8')).decode('utf-8')
    for name, content in {"sub.txt": final_str, "sub_ios.txt": b64_content, "sub_b64.txt": b64_content}.items():
        with open(os.path.join(EXPORT_DIR, name), "w", encoding="utf-8") as f: f.write(content)
    with open("count.txt", "w") as f: f.write(str(len(results[:TARGET_COUNT])))

if __name__ == "__main__": main()
