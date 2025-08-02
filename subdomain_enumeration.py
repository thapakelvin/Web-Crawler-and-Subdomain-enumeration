import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import socket
import threading
from queue import Queue

class SubdomainEnumeratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Subdomain Enumerator")
        self.root.geometry("600x500")

        # Domain input
        tk.Label(root, text="Target Domain:").pack(anchor="w", padx=10, pady=(10, 0))
        self.domain_entry = tk.Entry(root, width=50)
        self.domain_entry.pack(anchor="w", padx=10)

        # Wordlist file
        tk.Label(root, text="Subdomain Wordlist:").pack(anchor="w", padx=10, pady=(10, 0))
        frame = tk.Frame(root)
        frame.pack(anchor="w", padx=10)
        self.wordlist_path = tk.StringVar()
        tk.Entry(frame, textvariable=self.wordlist_path, width=40).pack(side="left")
        tk.Button(frame, text="Browse", command=self.browse_file).pack(side="left", padx=5)

        # Start button
        self.start_button = tk.Button(root, text="Start Enumeration", command=self.start_enumeration)
        self.start_button.pack(pady=10)

        # Output box
        tk.Label(root, text="Results:").pack(anchor="w", padx=10)
        self.output_box = scrolledtext.ScrolledText(root, height=20, width=70)
        self.output_box.pack(padx=10, pady=5)

        # Threading variables
        self.queue = Queue()
        self.threads = []
        self.stop_flag = False

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Wordlist",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if filename:
            self.wordlist_path.set(filename)

    def resolve_subdomain(self, subdomain):
        full_domain = f"{subdomain}.{self.domain}"
        try:
            ip = socket.gethostbyname(full_domain)
            self.queue.put(f"[+] Found: {full_domain} ({ip})\n")
        except socket.gaierror:
            # Domain does not resolve
            pass

    def worker(self):
        while not self.stop_flag:
            try:
                subdomain = self.subdomains_queue.get_nowait()
            except:
                break
            self.resolve_subdomain(subdomain)
            self.subdomains_queue.task_done()

    def update_output(self):
        while not self.queue.empty():
            line = self.queue.get()
            self.output_box.insert(tk.END, line)
            self.output_box.see(tk.END)
        if any(t.is_alive() for t in self.threads):
            self.root.after(100, self.update_output)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.output_box.insert(tk.END, "\nEnumeration completed.\n")

    def start_enumeration(self):
        self.domain = self.domain_entry.get().strip()
        wordlist_file = self.wordlist_path.get()

        if not self.domain:
            messagebox.showerror("Error", "Please enter a target domain.")
            return
        if not wordlist_file:
            messagebox.showerror("Error", "Please select a subdomain wordlist file.")
            return

        # Clear previous output
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, f"Starting subdomain enumeration on {self.domain}...\n\n")

        # Load wordlist
        try:
            with open(wordlist_file, "r") as f:
                subdomains = [line.strip() for line in f if line.strip()]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read wordlist file:\n{e}")
            return

        self.subdomains_queue = Queue()
        for sub in subdomains:
            self.subdomains_queue.put(sub)

        # Disable start button
        self.start_button.config(state=tk.DISABLED)

        # Start worker threads
        self.stop_flag = False
        self.threads = []
        thread_count = min(30, len(subdomains))  # max 30 threads or less

        for _ in range(thread_count):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

        # Start updating output box
        self.update_output()

if __name__ == "__main__":
    root = tk.Tk()
    app = SubdomainEnumeratorGUI(root)
    root.mainloop()
