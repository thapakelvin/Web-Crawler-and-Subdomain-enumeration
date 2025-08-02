import tkinter as tk
from tkinter import scrolledtext, messagebox
from threading import Thread
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import re
import datetime

class RecursiveWebCrawler:
    def __init__(self, start_url, max_depth, output_callback):
        self.start_url = start_url
        self.max_depth = max_depth
        self.output_callback = output_callback
        self.found_subdomains = set()
        self.discovered_links = set()
        self.javascript_files = set()

    def run(self):
        self.output_callback("=" * 80 + "\n")
        start_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.output_callback(f"Start time: {start_time}\n")
        self.output_callback(f"Starting URL: {self.start_url}\n")
        self.output_callback(f"Maximum depth: {self.max_depth}\n")
        self.output_callback("=" * 80 + "\n")

        self._crawl(self.start_url, current_depth=1)

        self.output_callback("\nDiscovered Subdomains:\n")
        if self.found_subdomains:
            for subdomain in self.found_subdomains:
                self.output_callback(f"{subdomain}\n")
        else:
            self.output_callback("None found\n")

        self.output_callback("\nDiscovered Links:\n")
        if self.discovered_links:
            for link in self.discovered_links:
                self.output_callback(f"{link}\n")
        else:
            self.output_callback("None found\n")

        self.output_callback("\nJavaScript Files:\n")
        if self.javascript_files:
            for js_file in self.javascript_files:
                self.output_callback(f"{js_file}\n")
        else:
            self.output_callback("None found\n")

        self.output_callback("=" * 80 + "\n")
        self.output_callback("Crawling completed.\n")

    def _crawl(self, url, current_depth):
        if current_depth > self.max_depth:
            return

        try:
            resp = requests.get(url, timeout=3, allow_redirects=True)
            resp.raise_for_status()
        except requests.RequestException as e:
            self.output_callback(f"Error fetching {url}: {str(e)}\n")
            return

        page = BeautifulSoup(resp.text, 'html.parser')

        # Extract anchor tags
        for link in page.find_all('a', href=True):
            href = link['href']
            # Check for subdomains
            subdomain_pattern = r"https?://([a-zA-Z0-9.-]+)"
            match = re.match(subdomain_pattern, href)
            if match and href not in self.found_subdomains:
                self.found_subdomains.add(href)
                self.output_callback(f"Found subdomain: {href}\n")
            else:
                # Handle relative/internal links
                full_url = urljoin(url, href)
                if full_url not in self.discovered_links:
                    self.discovered_links.add(full_url)
                    self.output_callback(f"Found link: {full_url}\n")
                    self._crawl(full_url, current_depth + 1)

        # Extract JavaScript files
        for script in page.find_all('script', src=True):
            js_url = urljoin(url, script['src'])
            self.javascript_files.add(js_url)
            self.output_callback(f"Found JavaScript file: {js_url}\n")

class CrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Recursive Web Crawler")
        self.root.geometry("700x600")

        self.url_label = tk.Label(root, text="Target URL:")
        self.url_label.pack()

        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack()

        self.depth_label = tk.Label(root, text="Crawl Depth:")
        self.depth_label.pack()

        self.depth_entry = tk.Entry(root, width=10)
        self.depth_entry.pack()

        self.start_button = tk.Button(root, text="Start Crawling", command=self.start_crawl_thread)
        self.start_button.pack()

        self.output_box = scrolledtext.ScrolledText(root, height=20, width=80)
        self.output_box.pack()

    def output(self, message):
        self.output_box.insert(tk.END, message)
        self.output_box.see(tk.END)

    def start_crawl_thread(self):
        url = self.url_entry.get().strip()
        depth = self.depth_entry.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a target URL.")
            return

        try:
            depth = int(depth)
            if depth <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive integer for depth.")
            return

        self.output_box.delete(1.0, tk.END)
        self.start_button.config(state=tk.DISABLED)

        thread = Thread(target=self.run_crawler, args=(url, depth), daemon=True)
        thread.start()

    def run_crawler(self, url, depth):
        crawler = RecursiveWebCrawler(url, depth, self.output)
        crawler.run()
        self.start_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = CrawlerGUI(root)
    root.mainloop()
