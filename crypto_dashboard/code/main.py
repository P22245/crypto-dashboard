import tkinter as tk
from tkinter import ttk
from CryptoDashboard import CryptoDashboard

def main():
    root = tk.Tk()

    style = ttk.Style()
    style.theme_use("clam")

    app = CryptoDashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
