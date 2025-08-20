"""
Navigator Package for system navigation tasks
"""
from tkinter import Tk
from tkinter.ttk import *
from tkinter.messagebox import *
from tkinter.filedialog import *
from pathlib import Path
import requests
import os
import platform
import threading
import json

__ver__ = "0.1.0"
__package__ = "navigator"
__author__ = "System"
__email__ = "Remaining@2925.com"
__description__ = "Navigator package for system navigation tasks"
__license__ = "MIT"

class Package:
    def __init__(self):
        self.name = "Navigator Plugin"
        self.version = __ver__
        self.author = __author__
        self.email = __email__
        self.description = __description__
        self.license = __license__
        self.progess = 0
        self.total = 100  # Total progress for the download, can be adjusted as needed

        # Loading pip libraries
        with open(Path(__file__).parent / "pip.json", "r", encoding="utf-8") as f:
            self.pip_libraries = json.load(f)
    
    def get_info(self):
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "email": self.email,
            "description": self.description,
            "license": self.license
        }
    
    # Main function of notebook tabs
    def download_python(self, bits="amd64"):
        amd64_url = "https://mirrors.huaweicloud.com/python/3.13.7/python-3.13.7-amd64.exe"
        arm64_url = "https://mirrors.huaweicloud.com/python/3.13.7/python-3.13.7-arm64.exe"
        win32_url = "https://mirrors.huaweicloud.com/python/3.13.7/python-3.13.7.exe"
        
        save_path = Path(__file__).parent.parent.parent / "downloads" / "python"

        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        if bits == "amd64":
            url = amd64_url
        elif bits == "arm64":
            url = arm64_url
        elif bits == "win32":
            url = win32_url
        else:
            raise ValueError("Unsupported architecture: {}".format(bits))

        try:
            responce = requests.get(url, stream=True)
            self.total = len(responce.iter_content(chunk_size=1024))
            
            if responce.status_code == 200:
                file_name = url.split("/")[-1]
                file_path = save_path / file_name
                
                with open(file_path, "wb") as file:
                    for chunk in responce.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            self.progess += len(chunk)
                
                print(f"[INFO] Python {bits} downloaded successfully: {file_path}")

                os.system(f'start "" "{file_path}"')  # Open the installer
                showinfo("下载完成", f"Python {bits} 下载完成\n已保存到: {file_path}")
            else:
                print(f"[ERROR] Failed to download Python {bits}. Status code: {responce.status_code}")
                raise Exception("Download failed with status code: {}".format(responce.status_code))
        except requests.exceptions.SSLError as e:
            print(f"[ERROR] SSL Error: {e}")
            print(f"[WARN]  Trying to download without SSL verification...")
            # Retry download without SSL verification
            try:
                responce = requests.get(url, stream=True, verify=False)
                if responce.status_code == 200:
                    file_name = url.split("/")[-1]
                    file_path = save_path / file_name
                    
                    with open(file_path, "wb") as file:
                        for chunk in responce.iter_content(chunk_size=1024):
                            if chunk:
                                file.write(chunk)
                                self.progess += len(chunk)
                    
                    print(f"[INFO] Python {bits} downloaded successfully: {file_path}")
                    os.system(f'start "" "{file_path}"')  # Open the installer
                    showinfo("下载完成", f"Python {bits} 下载完成\n已保存到: {file_path}")
                else:
                    raise Exception("Download failed with status code: {}".format(responce.status_code))
            except Exception as e:
                print(f"[ERROR] Download failed: {e}")
                showerror("下载失败", f"下载 Python {bits} 失败: {e}")
    
    def main(self):
        def __download_python():
            bits = bits_combobox.get()
            thread = threading.Thread(target=self.download_python, args=(bits,), daemon=True)
            thread.start()

        def __search():
            query = search_entry.get().lower()
            for item in pip_table.get_children():
                if item == query or query in pip_table.item(item, "values")[0].lower():
                    pip_table.selection_set(item)
                    pip_table.see(item)
                    return
            showinfo("搜索结果", f"未找到与 '{query}' 相关的库，请检查拼写或尝试其他关键词。\n\n如果认为无误，请在 GitHub 提交 issue 反馈。")

        print("[INFO] Navigator -- MIT LICENSE")
        print("[INFO] Starting...")


        try:
            # Mainwindow setup
            window = Tk()
            window.title("Navigator")
            window.geometry("400x300")
            window.resizable(False, True)

            # Add notebook
            notebook = Notebook(window)
            notebook.pack(expand=True, fill='both')
            
            # Python tab
            python_tab = Frame(notebook)
            notebook.add(python_tab, text="✨ 下载 Python")

            # Python download content
            download_title = Label(python_tab, text="下载 Python", font=("Microsoft Yahei UI", 12))
            download_title.grid(row=0, column=0, padx=10, pady=10)

            bits_combobox = Combobox(python_tab, values=["amd64", "arm64", "win32"], state="readonly")

            if platform.architecture()[0] == "64bit":
                bits_combobox.set("amd64")
            elif platform.architecture()[0] == "32bit":
                bits_combobox.set("win32")
            else:
                bits_combobox.set("arm64")
            
            bits_combobox.grid(row=1, column=0, padx=10, pady=10)

            download_button = Button(python_tab, text="下载 Python 3.13.7", command=__download_python, width=20)
            download_button.grid(row=1, column=1)

            splitter = Separator(python_tab, orient='horizontal')
            splitter.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

            # Pip download content (Placeholder)
            pip_title = Label(python_tab, text="下载 Pip", font=("Microsoft Yahei UI", 12))
            pip_title.grid(row=3, column=0, padx=10, pady=10)

            # Search bar and table for pip libraries
            search_entry = Entry(python_tab)
            search_entry.grid(row=4, column=0)
            search_button = Button(python_tab, text="搜索", command=__search)
            search_button.grid(row=4, column=1)

            pip_table = Treeview(python_tab, columns=("name", "des"), show="headings", height=5)
            pip_table.heading("name", text="库名")
            pip_table.heading("des", text="描述")
            pip_table.column("name", width=100)
            pip_table.column("des", width=250)
            pip_table.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

            for key, value in self.pip_libraries.items():
                pip_table.insert("", "end", values=(key, value))

            window.mainloop()
        
        except Exception as e:
            showerror("错误", f"程序运行时发生错误: {e}\n\n 请在 Github 提交 issue 反馈。")

if __name__ == "__main__":
    package = Package()
    package.main()
