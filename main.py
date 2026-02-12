import requests, base64, socket, ssl, random, re, os
from urllib.parse import urlparse, parse_qs, urlencode, unquote
from concurrent.futures import ThreadPoolExecutor

TARGET_COUNT = 50
TIMEOUT = 1.1 # تست سخت‌گیرانه برای کیفیت بالا
EXPORT_DIR = "export"

SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/trojan",
    "https://raw.githubusercontent.com/Lonewolf-sh/V2ray-Configs/main/All_Configs_Sub.txt"
]

def check_connection(target_ip, port, sni):
    try:
        context = ssl.create_default_context()
        context.check_hostname, context.verify_mode = False, ssl.CERT_NONE
        with socket.create_connection((target_ip, int(port)), timeout=TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=sni) as ssock: return True
    except: return False

def process_config(conf):
    try:
        conf = unquote(conf)
        parsed = urlparse(conf)
        user_info, host_port = parsed.netloc.split("@", 1)
        original_address, port = host_port.rsplit(":", 1) if ":" in host_port else (host_port, "443")
        params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        clean_ips = ["104.16.132.229", "104.18.2.161", "172.64.155.249", "104.17.3.184"]
        clean_ip = random.choice(clean_ips)
        if check_connection(clean_ip, port, original_address):
            params.update({'sni': original_address, 'host': original_address})
            return f"{parsed.scheme}://{user_info}@{clean_ip}:{port}?{urlencode(params)}#🚀_Rpix_Clean"
    except: pass
    return None

def main():
    if not os.path.exists(EXPORT_DIR): os.makedirs(EXPORT_DIR)
    raw_configs = list(set(re.findall(r'(?:vless|trojan)://[^\s]+', requests.get(random.choice(SOURCES)).text))) # انتخاب رندوم منبع برای تنوع در هر بار تکرار ۵ دقیقه‌ای
    
    # استخراج از همه منابع
    all_raw = set()
    for s in SOURCES:
        try: all_raw.update(re.findall(r'(?:vless|trojan)://[^\s]+', requests.get(s, timeout=10).text))
        except: continue

    with ThreadPoolExecutor(max_workers=80) as executor:
        results = list(filter(None, executor.map(process_config, list(all_raw)[:600])))

    final_results = results[:TARGET_COUNT]
    final_str = "\n".join(final_results)
    b64_content = base64.b64encode(final_str.encode('utf-8')).decode('utf-8')

    # متد اجباری برای آپدیت تاریخ فایل‌ها
    file_map = {"sub.txt": final_str, "sub_ios.txt": b64_content, "sub_b64.txt": b64_content}
    for name, content in file_map.items():
        with open(os.path.join(EXPORT_DIR, name), "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

    with open("count.txt", "w") as f: f.write(str(len(final_results)))

if __name__ == "__main__":
    main()
