
import aiohttp
import asyncio
import logging
import sqlite3
import csv
import socket
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from termcolor import colored

# Set up logging
logging.basicConfig(filename='link_extraction.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create SQLite database
def create_database():
    conn = sqlite3.connect('links.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

async def fetch_url(session, url):
    try:
        async with session.get(url) as response:
            status = response.status
            if 'text/html' in response.headers.get('Content-Type', ''):
                content = await response.text()
                return content, status
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
    return None, None

async def extract_links(session, base_url, depth=1, max_links=1000):
    all_links = set()
    to_visit = {base_url}
    visited = set()
    tasks = []

    while to_visit and depth > 0 and len(all_links) < max_links:
        new_to_visit = set()
        for url in to_visit:
            if url in visited:
                continue
            task = asyncio.create_task(process_url(session, url, new_to_visit, all_links, visited, base_url))
            tasks.append(task)
        await asyncio.gather(*tasks)
        to_visit = new_to_visit
        tasks = []
        depth -= 1

    return all_links

async def process_url(session, url, new_to_visit, all_links, visited, base_url):
    content, status = await fetch_url(session, url)
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href.strip())
                if is_valid_url(full_url) and is_internal_url(base_url, full_url):
                    if full_url not in all_links:
                        all_links.add(full_url)
                        new_to_visit.add(full_url)
        await store_link(url, status)
    visited.add(url)

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc)

def is_internal_url(base_url, url):
    base_domain = urlparse(base_url).netloc
    link_domain = urlparse(url).netloc
    return base_domain == link_domain

async def check_robots(session, base_url):
    robots_url = urljoin(base_url, '/robots.txt')
    try:
        async with session.get(robots_url) as response:
            if response.status == 200:
                content = await response.text()
                disallowed = [line.split(':')[1].strip() for line in content.split('\n') if line.startswith('Disallow')]
                return disallowed
    except Exception as e:
        logging.error(f"Error fetching robots.txt from {base_url}: {e}")
    return []

async def store_link(url, status):
    conn = sqlite3.connect('links.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO links (url, status) VALUES (?, ?)', (url, status))
    conn.commit()
    conn.close()

def export_to_csv(file_name='links.csv'):
    conn = sqlite3.connect('links.db')
    c = conn.cursor()
    c.execute('SELECT url, status FROM links')
    rows = c.fetchall()
    conn.close()
    
    with open(file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL', 'Status'])
        writer.writerows(rows)

def show_help():
    print("How to use the tool:")
    print("1. Run the program.")
    print("2. Choose option 1 to start scanning, option 2 for tool information, option 3 for port scanning, or option 4 for IP address.")
    print("3. If you choose option 1, provide the base URL, the number of links to extract, and the scan depth.")
    print("4. After the scan is complete, you can choose to export the results to a CSV file.")
    print("5. Option 3 will scan the specified IP address for open ports.")
    print("6. Option 4 will resolve the domain to its IP address using ping.")

def show_info():
    print("Tool Information:")
    print("N-link Tool is a link extraction tool for a specific website.")
    print("You can specify the scan depth and the number of links you want to extract.")
    print("Results are stored in an SQLite database and can be exported to a CSV file.")
    print("Additionally, you can scan ports and resolve IP addresses.")

def scan_ports(ip_address, ports):
    import socket
    open_ports = {}
    if ports == 'all':
        ports = range(1, 1000)
    else:
        ports = list(map(int, ports.split(',')))
        
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip_address, port))
        if result == 0:
            open_ports[port] = 'Open'
        else:
            open_ports[port] = 'Closed'
        sock.close()
    return open_ports

def get_ip_from_domain(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except socket.error:
        return None

async def main():
    print("""""
                                                                           rrrrrr
   rrrrrr                                                                   rr  rr
   rrrrrr          rrrrrrrrrrrrrrrrr                                        rrrrrr                  rrrrrrrrrr
   rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr
   rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr KURDIASTAN - AMUDA - NART rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr
   rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr
   rrrrrr          rrrrrrrrrrrrrrrrrr                 rrrrrrrr    /rr                               rrrrrrrrr
   rrrrrr                     rrrrrrr                 rrrrrrrr   / rr
                              rrrrrrr                 rrrrrrrr  /  rr
                              rrrrrrr                 rrrrrrrrrrrrrrr
                                                      rrrrrrrr
                                                      rrrrrrrr
   """)

    print(colored("*************************************************", 'red',))
    print(colored("*              Welcome to N-link Tool           *", 'white', attrs=['bold']))
    print(colored("*        Unleash the Power of Link Extraction   *", 'yellow', attrs=['bold']))
    print(colored("*       Precision and Excellence in Every Scan  *", 'white', attrs=['bold']))
    print(colored("*        Follow Instagram | @_hlvv for Updates  *", 'green', attrs=['bold']))
    print(colored("*************************************************", 'green',))

    while True:
        print("\nChoose an option:")
        print("1. Start Scan")
        print("2. Tool Information")
        print("3. Port Scanning")
        print("4. Get IP Address")
        print("0. How to Use")
        choice = input("Select an option (0/1/2/3/4): ").strip()

        if choice == '1':
            # Request user input to start scanning
            base_url = input("Enter the base URL to start extraction: ").strip()
            max_links = int(input("Enter the maximum number of links to extract (default is 1000): ").strip() or 1000)
            depth = int(input("Enter the depth of scan (default is 1): ").strip() or 1)
            export_choice = input("Would you like to export the results to CSV? (yes/no): ").strip().lower() == 'yes'

            create_database()

            async with aiohttp.ClientSession() as session:
                print(colored("🔍 Initiating Advanced Scan at: " + base_url, 'yellow', attrs=['bold']))

                disallowed_paths = await check_robots(session, base_url)
                print(f"Disallowed paths from robots.txt: {disallowed_paths}")

                print(colored("🔗 Extracting links...", 'cyan', attrs=['bold']))
                links = await extract_links(session, base_url, depth, max_links)
                if links:
                    print(colored("✅ Links extracted successfully!", 'green', attrs=['bold']))
                else:
                    print(colored("❌ No links found.", 'yellow', attrs=['bold']))

                print(colored("🔗 All links:", 'cyan', attrs=['bold']))
                for i, link in enumerate(links, start=1):
                    print(f"{i}. {link}")
                if export_choice:
                    export_to_csv()
                    print(colored("📥 Exported results to links.csv", 'green', attrs=['bold']))

        elif choice == '2':
            show_info()

        elif choice == '3':
            ip_address = input("Enter the IP address to scan for open ports: ").strip()
            scan_choice = input("Enter ports to scan (comma-separated) or type 'all' to scan all ports: ").strip()
            open_ports = scan_ports(ip_address, scan_choice)
            print(colored("Port Scan Results:", 'cyan', attrs=['bold']))
            for port, status in open_ports.items():
                print(f"Port {port}: {status}")

        elif choice == '4':
            domain = input("Enter the domain to get its IP address (without http:// or https:// and .com): ").strip()
            ip_address = get_ip_from_domain(domain)
            if ip_address:
                print(f"The IP address for domain {domain} is {ip_address}")
            else:
                print(f"Could not resolve IP address for domain {domain}")

        elif choice == '0':
            show_help()

        else:
            print("Invalid option, please select a valid option.")

if __name__ == '__main__':
    asyncio.run(main())