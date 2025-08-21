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

__ver__ = "v0.1.2 (last commit: 49ca003)"
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
        self.pip_libraries = {
            "pyinstaller": "Python 打包工具",
            "tqdm": "Python 进度条库",
            "requests": "Python HTTP 库",
            "lxml": "Python XML 和 HTML 解析库",
            "pillow": "Python 图像处理库",
            "numpy": "Python 科学计算库",
            "pandas": "Python 数据分析库",
            "matplotlib": "Python 绘图库",
            "scipy": "Python 科学计算库",
            "flask": "Python Web 框架",
            "django": "Python Web 框架",
            "fastapi": "高性能 Python Web 框架",
            "sqlalchemy": "Python SQL 工具包和对象关系映射器",
            "pytest": "Python 测试框架",
            "black": "Python 代码格式化工具",
            "mypy": "Python 静态类型检查器",
            "jupyter": "交互式计算环境",
            "notebook": "Jupyter 笔记本服务器",
            "ipython": "交互式 Python 解释器",
            "virtualenv": "Python 虚拟环境工具",
            "pipenv": "Python 包和虚拟环境管理工具",
            "poetry": "Python 包和依赖管理工具",
            "sphinx": "Python 文档生成器",
            "twine": "Python 包上传工具",
            "setuptools": "Python 包打包工具",
            "wheel": "Python 包打包格式",
            "cython": "Python 和 C 混合编程工具",
            "pyyaml": "Python YAML 解析库",
            "cryptography": "Python 加密库",
            "paramiko": "Python SSH 库",
            "fabric": "Python 远程执行工具",
            "celery": "Python 分布式任务队列",
            "redis": "Python Redis 客户端",
            "sqlparse": "Python SQL 解析库",
            "pytest-cov": "Pytest 代码覆盖率插件",
            "coverage": "Python 代码覆盖率工具",
            "flake8": "Python 代码风格检查工具",
            "pylint": "Python 代码静态分析工具",
            "autopep8": "Python 代码自动格式化工具",
            "isort": "Python 导入排序工具",
            "rope": "Python 重构库",
            "jedi": "Python 自动补全和静态分析库",
            "watchdog": "Python 文件系统事件监控库",
            "httpx": "Python HTTP 客户端",
            "starlette": "轻量级 ASGI 框架",
            "uvicorn": "高性能 ASGI 服务器",
            "gunicorn": "Python WSGI HTTP 服务器",
            "gevent": "Python 异步网络库",
            "eventlet": "Python 并发网络库",
            "twisted": "Python 事件驱动网络引擎",
            "bottle": "轻量级 Python Web 框架",
            "cherrypy": "Python 面向对象的 Web 框架",
            "hug": "Python API 框架",
            "connexion": "Python REST API 框架",
            "falcon": "高性能 Python Web 框架",
            "pydantic": "数据验证和设置管理库",
            "orjson": "快速 JSON 序列化库",
            "ujson": "Ultra fast JSON 库",
            "simplejson": "简单的 JSON 库",
            "pycryptodome": "Python 加密库",
            "bcrypt": "Python 密码哈希库",
            "argon2-cffi": "Python Argon2 密码哈希库",
            "passlib": "Python 密码哈希库",
            "pyjwt": "Python JSON Web Token 库",
            "python-dotenv": "Python 环境变量加载库",
            "loguru": "Python 日志库",
            "structlog": "结构化日志库",
            "rich": "Python 富文本和格式化库",
            "textual": "Python 终端用户界面框架",
            "prompt-toolkit": "Python 交互式命令行界面库",
            "click": "Python 命令行界面创建库",
            "typer": "基于类型注解的 Python 命令行界面库",
            "fire": "自动生成命令行界面的库",
            "argparse": "Python 命令行参数解析库",
            "docopt": "Python 命令行接口描述库",
            "pydoc": "Python 文档生成器",
            "mkdocs": "静态站点生成器",
            "mkdocs-material": "MkDocs 主题",
            "sphinx-rtd-theme": "Sphinx 主题",
            "alabaster": "Sphinx 主题",
            "nbsphinx": "Sphinx 扩展，用于包含 Jupyter 笔记本",
            "sphinx-autodoc-typehints": "Sphinx 扩展，用于自动生成类型注解文档",
            "sphinxcontrib-napoleon": "Sphinx 扩展，支持 Google 和 NumPy 风格的 docstring",
            "pytest-django": "Pytest Django 插件",
            "pytest-flask": "Pytest Flask 插件",
            "pytest-asyncio": "Pytest 异步支持插件",
            "pytest-mock": "Pytest Mock 插件",
            "pytest-xdist": "Pytest 并行测试插件",
            "pytest-benchmark": "Pytest 性能测试插件",
            "pytest-sugar": "美化 Pytest 输出",
            "pytest-html": "生成 HTML 测试报告",
            "pytest-cases": "Pytest 测试用例管理插件",
            "pytest-timeout": "Pytest 超时插件",
            "pytest-rerunfailures": "Pytest 失败重试插件",
            "pytest-ordering": "Pytest 测试顺序插件",
            "pytest-env": "Pytest 环境变量插件",
            "pytest-profiling": "Pytest 性能分析插件",
            "pytest-lazy-fixture": "Pytest 懒加载夹具插件",
            "bs4": "Beautiful Soup 4 HTML 解析库",
            "scrapy": "Python 爬虫框架",
            "selenium": "Python 浏览器自动化库",
            "playwright": "Python 浏览器自动化库",
            "httpie": "命令行 HTTP 客户端",
            "mitmproxy": "交互式中间人代理",
            "locust": "Python 负载测试工具",
            "jmespath": "JSON 查询库",
            "jsonschema": "JSON 模式验证库",
            "pydash": "Python 实用工具库",
            "toolz": "函数式编程工具库",
            "cytoolz": "Cython 优化的函数式编程工具库",
            "boltons": "Python 实用工具库",
            "more-itertools": "扩展的迭代器工具库",
            "funcy": "函数式编程工具库",
            "dataclasses": "Python 数据类库 (Python 3.7+ 内置)",
            "attrs": "Python 属性管理库",
            "pyrsistent": "不可变数据结构库",
            "pytorch": "PyTorch 深度学习框架",
            "tensorflow": "TensorFlow 深度学习框架",
            "keras": "高级神经网络 API",
            "transformers": "自然语言处理库",
            "datasets": "机器学习数据集库",
            "opencv-python": "OpenCV 计算机视觉库",
            "scikit-learn": "机器学习库",
            "xgboost": "梯度提升库",
            "lightgbm": "LightGBM 梯度提升库",
            "catboost": "CatBoost 梯度提升库",
            "fastai": "深度学习库",
            "albumentations": "图像增强库",
            "imgaug": "图像增强库",
            "nltk": "自然语言处理库",
            "openai": "OpenAI API 客户端",
            "langchain": "语言模型链库",
            "streamlit": "数据应用快速开发框架",
            "dash": "数据可视化应用框架",
            "pygame": "Python 游戏开发库",
            "pydub": "音频处理库",
            "moviepy": "视频编辑库",
            "ffmpeg-python": "FFmpeg 命令行工具的 Python 接口",
            "pyqt5": "Python Qt5 绑定",
            "pyside2": "Python Qt5 绑定",
            "kivy": "Python 多点触控应用框架"
        }
        
        # Load app list
        self.app_list = {
            "Atom": [
                "https://mirrors.tuna.tsinghua.edu.cn/github-release/atom/atom/LatestRelease/AtomSetup-x64.exe",
                "https://mirrors.tuna.tsinghua.edu.cn/github-release/atom/atom/LatestRelease/AtomSetup.exe"
            ],
            "Blender": [
                "https://mirrors.tuna.tsinghua.edu.cn/blender/blender-release/Blender4.5/blender-4.5.0-windows-x64.msi",
                False
            ],
            "Git": [
                "https://mirrors.tuna.tsinghua.edu.cn/github-release/git-for-windows/git/LatestRelease/Git-2.51.0-64-bit.exe",
                False
            ],
            "Vscode": [
                "https://mirrors.tuna.tsinghua.edu.cn/github-release/VSCodium/vscodium/LatestRelease/VSCodium-x64-1.103.15539.msi",
                "https://mirrors.tuna.tsinghua.edu.cn/github-release/VSCodium/vscodium/LatestRelease/VSCodium-ia32-1.103.15539.msi"
            ],
            "Docker": [
                "https://mirrors.tuna.tsinghua.edu.cn/docker-ce/win/static/stable/x86_64/docker-28.3.3.zip",
                False
            ],
            "Vitrual box": [
                "https://mirrors.tuna.tsinghua.edu.cn/virtualbox/7.2.0/VirtualBox-7.2.0-170228-Win.exe",
                False
            ],
            "Wireshark": [
                "https://mirrors.tuna.tsinghua.edu.cn/wireshark/win64/Wireshark-latest-x64.exe",
                False
            ],
            "Rustdesk": [
                False,
                "https://mirrors.tuna.tsinghua.edu.cn/github-release/rustdesk/rustdesk/LatestRelease/rustdesk-1.4.1-x86_64.exe"
            ]
        }
    
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
        
        save_path = Path(__file__).parent.parent / "downloads" / "python"

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

    def download_application(self, amd64_url, win32_url, name, bits="amd64"):
        save_path = Path(__file__).parent.parent / "downloads" / name

        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        if bits == "amd64":
            url = amd64_url
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
                
                print(f"[INFO] Application {bits} downloaded successfully: {file_path}")

                os.system(f'start "" "{file_path}"')  # Open the installer
                showinfo("下载完成", f"应用 {bits} 下载完成\n已保存到: {file_path}")
            else:
                print(f"[ERROR] Failed to download application {bits}. Status code: {responce.status_code}")
                raise Exception("Download failed with status code: {}".format(responce.status_code))
        except requests.exceptions.SSLError as e:
            print(f"[ERROR] SSL Error: {e}")
            print(f"[WARN]  Trying to download without SSL verification...")
            # Retry download without SSL verification
            try:
                responce = requests.get(url, stream=True, verify=False)
                file_name = url.split("/")[-1]
                file_path = save_path / file_name
                
                with open(file_path, "wb") as file:
                    for chunk in responce.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            self.progess += len(chunk)
                
                print(f"[INFO] Application {bits} downloaded successfully: {file_path}")
                os.system(f'start "" "{file_path}"')  # Open the installer
                showinfo("下载完成", f"应用 {bits} 下载完成\n已保存到: {file_path}")
            except Exception as e:
                print(f"[ERROR] Download failed: {e}")
                showerror("下载失败", f"下载应用 {bits} 失败: {e}")
    
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
            pip_table.bind("<Double-1>", lambda e: os.system(f'pip install {pip_table.item(pip_table.selection()[0], "values")[0]}'))
            pip_table.heading("name", text="库名")
            pip_table.heading("des", text="描述")
            pip_table.column("name", width=100)
            pip_table.column("des", width=250)
            pip_table.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

            for key, value in self.pip_libraries.items():
                pip_table.insert("", "end", values=(key, value))
            
            # Application download tab (Placeholder)
            app_tab = Frame(notebook)
            notebook.add(app_tab, text="🚀 下载应用")

            app_title = Label(app_tab, text="下载应用", font=("Microsoft Yahei UI", 12))
            app_title.grid(row=0, column=0, padx=10, pady=10)

            # Application buttons
            row = 1
            column = 0
            for app_name, app_info in self.app_list.items():
                amd64_url = app_info[0]
                win32_url = app_info[1]
                
                if amd64_url != False:
                    app_button = Button(app_tab, text=f"下载 {app_name} (amd64)", command=lambda url=amd64_url: self.download_application(url, win32_url, app_name, "amd64"))
                if win32_url != False:
                    app_button = Button(app_tab, text=f"下载 {app_name} (win32)", command=lambda url=win32_url: self.download_application(amd64_url, url, app_name, "win32"))

                app_button.grid(row=row, column=column, padx=10, pady=5, sticky="ew")
                column += 1

                if column >= 2:
                    row += 1
                    column = 0
            
            # Help tab
            help_tab = Frame(notebook)
            notebook.add(help_tab, text="❓ 帮助")

            version_label = Label(help_tab, text=f"Navigator 版本: {self.version}")
            version_label.pack(pady=10)
            author_label = Label(help_tab, text=f"作者: {self.author} ({self.email})")
            author_label.pack(pady=10)
            license_label = Label(help_tab, text=f"许可证: {self.license}")
            license_label.pack(pady=10)
            desc_label = Label(help_tab, text=self.description, wraplength=300, justify="left")
            desc_label.pack(pady=10)
            repo_label = Label(help_tab, text="源代码已在 Gitcode Github Gitee 三方平台上同步开放", wraplength=300, justify="left")
            repo_label.pack(pady=10)

            # Start the main loop
            window.mainloop()
        
        except Exception as e:
            showerror("错误", f"程序运行时发生错误: {e} \n\n 请在 Github 提交 issue 反馈，我们会尽快处理。")

if __name__ == "__main__":
    package = Package()
    package.main()
