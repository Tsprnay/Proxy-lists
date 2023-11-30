import requests
import json
import os
import time
import random
import re
import ipaddress

with open('sites.json') as f:
    sites = json.load(f)


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
    if os.path.exists(f'{file_name}.txt'):
        os.remove(f'{file_name}.txt')


def scrape_proxies(type):
    for site in sites[type]:
        try:
            r = requests.get(site, timeout=5)
            with open(f"proxies/{type}.txt", "a") as f:
                f.write("\n" + r.text)
        except Exception as e:
            print(f'Error scraping proxies from {site}: {e}')
        time.sleep(1)


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
        return 0 <= int(port) <= 65535 and len(ip) <= 15  # Check both port validity and IP length
    except ValueError:
        return False


def validate_ips(file_name):
    ips_with_ports = extract_ips_with_ports(file_name)
    valid_ips = [ip for ip in ips_with_ports if validate_ip(ip.split(':')[0]) and validate_ports(ip)]

    with open(file_name, 'w') as f:
        f.write('\n'.join(valid_ips))


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
                out_file.write(in_file.read())


if not os.path.exists('proxies'):
    os.makedirs('proxies')

remove_exists('proxies/socks4')
remove_exists('proxies/socks5')
remove_exists('proxies/http')
remove_exists('proxies/https')

scrape_proxies('socks4')
scrape_proxies('socks5')
scrape_proxies('http')
scrape_proxies('https')

remove_empty_lines('proxies/socks4.txt')
remove_empty_lines('proxies/socks5.txt')
remove_empty_lines('proxies/http.txt')
remove_empty_lines('proxies/https.txt')

remove_duplicates('proxies/socks4.txt')
remove_duplicates('proxies/socks5.txt')
remove_duplicates('proxies/http.txt')
remove_duplicates('proxies/https.txt')

validate_ips('proxies/socks4.txt')
validate_ips('proxies/socks5.txt')
validate_ips('proxies/http.txt')
validate_ips('proxies/https.txt')

randomize_proxies('proxies/socks4.txt')
randomize_proxies('proxies/socks5.txt')
randomize_proxies('proxies/http.txt')
randomize_proxies('proxies/https.txt')

combine_proxy_files('proxies/all.txt', 'proxies/socks4.txt', 'proxies/socks5.txt', 'proxies/http.txt',
                    'proxies/https.txt')

remove_duplicates('proxies/all.txt')
remove_empty_lines('proxies/all.txt')
randomize_proxies('proxies/all.txt')

ips_without_ports = extract_ips_without_ports('proxies/all.txt')

with open('proxies/all_no_ports.txt', 'w') as f:
    f.write('\n'.join(ips_without_ports))

validate_ips('proxies/all.txt')
