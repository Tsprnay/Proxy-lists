import requests
import json
import os
import time
import random
import re
import ipaddress
import shutil

with open('sites.json') as f:
    sites = json.load(f)

def clean_proxy_format(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()

    cleaned_lines = []
    for line in lines:
        parts = line.split(':')
        if len(parts) >= 2:
            cleaned_line = parts[0] + ':' + parts[1]
            cleaned_lines.append(cleaned_line.strip())

    with open(file_name, 'w') as f:
        f.writelines('\n'.join(cleaned_lines))

def remove_duplicates(file_name):
    lines_seen = set()
    new_file_name = file_name + ".tmp"
    outfile = open(new_file_name, "w")
    for line in open(file_name, "r"):
        if line not in lines_seen:
            outfile.write(line)
            lines_seen.add(line)
    outfile.close()
    os.remove(file_name)
    os.rename(new_file_name, file_name)


def remove_empty_lines(file_name):
    with open(file_name, 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        f.writelines(line for line in lines if line.strip())
        f.truncate()


def remove_exists(file_name):
    if os.path.exists(f'proxies/{file_name}.txt'):
        os.remove(f'proxies/{file_name}.txt')
    if os.path.exists(f'proxies/sorted/{file_name}.txt'):
        os.remove(f'proxies/sorted/{file_name}.txt')
    if os.path.exists('proxies/all.txt'):
        os.remove('proxies/all.txt')
    if os.path.exists('proxies/sorted/all.txt'):
        os.remove('proxies/sorted/all.txt')
    if os.path.exists('proxies/all_no_ports.txt'):
        os.remove('proxies/all_no_ports.txt')
    if os.path.exists('proxies/sorted/all_no_ports.txt'):
        os.remove('proxies/sorted/all_no_ports.txt')


def scrape_proxies(type):
    success = False
    for site in sites[type]:
        try:
            r = requests.get(site, timeout=5)
            proxies = r.text.split('\n')
            valid_proxies = [proxy for proxy in proxies if len(proxy) <= 21]
            with open(f"proxies/{type}.txt", "a") as f:
                f.write("\n" + '\n'.join(valid_proxies))
            print(f'Successfully scraped {len(valid_proxies)} proxies from {site}')
            success = True
        except requests.exceptions.RequestException as e:
            print(f'Error scraping proxies from {site}: {e}')
            print('Skipping this site and moving to the next one...')
        time.sleep(0.5)
    if not success:
        print('Failed to scrape proxies from all sites.')
        sys.exit(1)

def extract_ips_with_ports(file_name):
    with open(file_name) as f:
        ips_with_ports = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]+\b', f.read())
    return ips_with_ports


def extract_ips_without_ports(file_name):
    ips_with_ports = extract_ips_with_ports(file_name)
    ips_without_ports = [ip.split(':')[0] for ip in ips_with_ports]
    return ips_without_ports


def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def validate_ports(ip_with_port):
    ip, port = ip_with_port.split(':')
    try:
        return 0 <= int(port) <= 65535 and len(ip) <= 15
    except ValueError:
        return False


def validate_ips(file_name):
    ips_with_ports = extract_ips_with_ports(file_name)
    valid_ips = []
    for ip in ips_with_ports:
        ip_parts = ip.split(':')
        if len(ip) <= 21 and len(ip_parts) == 2 and validate_ip(ip_parts[0]) and validate_ports(ip):
            valid_ips.append(ip)

    with open(file_name, 'w') as f:
        f.write('\n'.join(valid_ips))

def remove_long_lines(file_name, max_length):
    with open(file_name, 'r') as f:
        lines = f.readlines()

    with open(file_name, 'w') as f:
        for line in lines:
            if len(line.strip()) <= max_length:
                f.write(line)

def randomize_proxies(file_name):
    with open(file_name) as f:
        lines = f.readlines()
        random.shuffle(lines)
        with open(file_name, 'w') as f:
            f.writelines(lines)

def combine_proxy_files(output_file, *input_files):
    with open(output_file, 'w') as out_file:
        for input_file in input_files:
            with open(input_file) as in_file:
                out_file.write(in_file.read().strip() + '\n')

def duplicate_and_sort_proxies(file_name):
    sorted_folder_path = 'proxies/sorted'
    sorted_file_path = os.path.join(sorted_folder_path, os.path.basename(file_name))

    shutil.copyfile(file_name, sorted_file_path)

    with open(sorted_file_path, 'r') as f:
        proxies = sorted(f.readlines())

    with open(sorted_file_path, 'w') as f:
        f.writelines(proxies)

def remove_unwanted_proxies(file_name):
    unwanted_ips = {'0.0.0.0', '127.0.0.1', '1.1.1.1', '8.8.8.8', '8.8.4.4'}
    with open(file_name, 'r') as f:
        proxies = f.readlines()

    proxies = [proxy for proxy in proxies if proxy.split(':')[0] not in unwanted_ips]

    with open(file_name, 'w') as f:
        f.writelines(proxies)

def process_proxies():
    proxy_types = ['socks4', 'socks5', 'http', 'https']
    proxy_files = {ptype: f'proxies/{ptype}.txt' for ptype in proxy_types}

    if not os.path.exists('proxies'):
        os.makedirs('proxies')
    if not os.path.exists('proxies/sorted'):
        os.makedirs('proxies/sorted')

    for ptype in proxy_types:
        remove_exists(ptype)

    for ptype in proxy_types:
        scrape_proxies(ptype)

    for file_name in proxy_files.values():
        clean_proxy_format(file_name)
        remove_empty_lines(file_name)
        remove_duplicates(file_name)
        remove_unwanted_proxies(file_name)
        randomize_proxies(file_name)
        validate_ips(file_name)
        remove_long_lines(file_name, 21)

    combine_proxy_files('proxies/all.txt', *proxy_files.values())

    remove_duplicates('proxies/all.txt')
    remove_empty_lines('proxies/all.txt')
    randomize_proxies('proxies/all.txt')

    ips_without_ports = extract_ips_without_ports('proxies/all.txt')
    with open('proxies/all_no_ports.txt', 'w') as f:
        f.write('\n'.join(ips_without_ports))

    remove_duplicates('proxies/all_no_ports.txt')
    validate_ips('proxies/all.txt')
    remove_long_lines('proxies/all.txt', 21)

    for file_name in proxy_files.values():
        duplicate_and_sort_proxies(file_name)
    duplicate_and_sort_proxies('proxies/all.txt')
    duplicate_and_sort_proxies('proxies/all_no_ports.txt')

process_proxies()
