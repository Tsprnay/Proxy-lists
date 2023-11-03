import requests
import json
import os
import time
import random

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


def randomize_proxies(file_name):
    with open(file_name) as f:
        lines = f.readlines()
        random.shuffle(lines)
        with open(file_name, 'w') as f:
            f.writelines(lines)

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

randomize_proxies('proxies/socks4.txt')
randomize_proxies('proxies/socks5.txt')
randomize_proxies('proxies/http.txt')
randomize_proxies('proxies/https.txt')
