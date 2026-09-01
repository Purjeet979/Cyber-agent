import subprocess
import urllib.request
import json
import time
import socket
import re

# Dashboard URL
API_URL = "http://localhost:5000/api/v1/alerts"

# Ignore noisy domains to avoid spamming the LLM and rate limits
WHITELIST = ["microsoft", "windows", "google", "apple", "mozilla", "local", "arpa"]

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_dns_cache():
    try:
        output = subprocess.check_output(["ipconfig", "/displaydns"], text=True, stderr=subprocess.STDOUT)
        domains = set()
        # Parse Record Names
        for line in output.split('\n'):
            if "Record Name" in line:
                match = re.search(r"Record Name[^:]+:\s*(\S+)", line)
                if match:
                    domain = match.group(1).lower()
                    
                    # Basic noise filtering
                    is_noisy = any(w in domain for w in WHITELIST)
                    if not is_noisy:
                        domains.add(domain)
        return domains
    except Exception as e:
        print(f"[-] Could not read DNS cache: {e}")
        return set()

def send_log(domain, ip):
    log_msg = f"EndpointAgent: DNS Request from {ip} to resolve domain {domain}"
    print(f"[+] Sending log to Kalki: {domain}")
    
    data = json.dumps({"raw_log": log_msg}).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, headers={"Content-Type": "application/json"}, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            response.read()
    except Exception as e:
        print(f"[-] Failed to send alert: {e}")

def run_agent_loop(is_running_func=lambda: True):
    print("==================================================")
    print("🛡️ Kalki Real-time Endpoint Agent (Windows)")
    print("==================================================")
    print("Monitoring live DNS cache for new connections...\n")
    
    local_ip = get_local_ip()
    seen_domains = get_dns_cache()
    
    # Optional: flush DNS cache initially so we only get fresh requests
    # subprocess.call(["ipconfig", "/flushdns"])
    
    while is_running_func():
        try:
            current_domains = get_dns_cache()
            
            # Find new domains that weren't in the cache previously
            new_domains = current_domains - seen_domains
            
            for domain in new_domains:
                send_log(domain, local_ip)
            
            # Update our seen list
            seen_domains = current_domains
            
            time.sleep(3) # Check every 3 seconds
        except Exception as e:
            print(f"Agent error: {e}")
            break
    print("\nStopping agent.")

if __name__ == "__main__":
    try:
        run_agent_loop()
    except KeyboardInterrupt:
        print("Agent stopped by user.")
