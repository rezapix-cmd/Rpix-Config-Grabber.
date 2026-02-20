import requests, base64, socket, ssl, random, re, os
from urllib.parse import urlparse, parse_qs, urlencode, unquote, quote
from concurrent.futures import ThreadPoolExecutor

TARGET_COUNT = 50
TIMEOUT = 1.5
EXPORT_DIR = "export"

SOURCES = [
    "https://raw.githubusercontent.com/rezapix-cmd/Rpix-Config-Grabber/main/SOURCES.txt",
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
    try:
        if not os.path.exists(EXPORT_DIR): 
            os.makedirs(EXPORT_DIR)
            print(f"✅ پوشه {EXPORT_DIR} ایجاد شد")
        
        all_raw = set()
        print("📥 دریافت موارد از منابع...")
        
        for s in SOURCES:
            try:
                res = requests.get(s, timeout=10).text
                found = re.findall(r'(?:vless|trojan)://[^\s]+', decode_base64_if_needed(res))
                all_raw.update(found)
                print(f"   ✅ {len(found)} مورد پیدا شد")
            except Exception as e: 
                print(f"   ❌ خطا: {e}")
                continue
        
        if not all_raw:
            print("❌ هیچ موردی استخراج نشد!")
            return False
        
        print(f"📊 کل موارد: {len(all_raw)}")
        
        raw_list = list(all_raw)
        random.shuffle(raw_list)
        
        print(f"⚙️ پردازش {len(raw_list[:600])} مورد...")
        with ThreadPoolExecutor(max_workers=25) as executor:
            results = list(filter(None, executor.map(process_config, raw_list[:600])))
        
        if not results:
            print("❌ هیچ موردی پردازش نشد!")
            return False
        
        print(f"✅ {len(results)} مورد آماده شد")
        
        final_str = "\n".join(results[:TARGET_COUNT])
        b64_content = base64.b64encode(final_str.encode('utf-8')).decode('utf-8')
        
        files_to_write = {
            "sub.txt": final_str, 
            "sub_ios.txt": b64_content, 
            "sub_b64.txt": b64_content
        }
        
        for name, content in files_to_write.items():
            file_path = os.path.join(EXPORT_DIR, name)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            size = os.path.getsize(file_path)
            if size > 0:
                print(f"✅ {name}: {size} بایت")
            else:
                print(f"❌ {name} خالی است!")
                return False
        
        with open("count.txt", "w") as f:
            f.write(str(len(results[:TARGET_COUNT])))
        print(f"✅ count.txt: {len(results[:TARGET_COUNT])} مورد")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False

if __name__ == "__main__": 
    success = main()
    exit(0 if success else 1)
