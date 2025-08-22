"""
Navigator Package for system navigation tasks
"""
from tkinter import Tk, Toplevel, Text
from tkinter.ttk import *
from tkinter.messagebox import *
from tkinter.filedialog import *
from pathlib import Path
from typing import Tuple
import requests
import os
import platform
import threading
import ast
import keyword
import builtins
import io
import tokenize
import re


__ver__ = "v1.0.2"
__package__ = "navigator"
__author__ = "System"
__email__ = "Remaining@2925.com"
__description__ = "Navigator package for system navigation tasks"
__license__ = "MIT"

class Theme:
    Light = {
        "base": {
            "background": "#FFFFFF",
            "foreground": "#24292E",
            "insertbackground": "#24292E",
            "selectbackground": "#C8C8FA",
            "selectforeground": "#24292E"
        },
        "keyword": "#D73A49",
        "control": "#D73A49",
        "operator": "#24292E",
        "punctuation": "#24292E",
        
        "class": "#6F42C1",
        "function": "#6F42C1",
        "method": "#6F42C1",
        "variable": "#24292E",
        "parameter": "#24292E",
        "property": "#24292E",
        
        "string": "#032F62",
        "number": "#005CC5",
        "boolean": "#005CC5",
        "null": "#005CC5",
        "constant": "#005CC5",
        
        "comment": "#6A737D",
        "docstring": "#6A737D",
        "todo": "#FF8C00",
        
        "decorator": "#6F42C1",
        "builtin": "#005CC5",
        "self": "#24292E",
        "namespace": "#6F42C1",
        
        "type": "#6F42C1",
        "type_annotation": "#6F42C1",
        "interface": "#6F42C1"
    } 

    Dark = {
        "base": {
            "background": "#0D1117",
            "foreground": "#C9D1D9",
            "insertbackground": "#C9D1D9",
            "selectbackground": "#363D4A",
            "selectforeground": "#C9D1D9"
        },
        "keyword": "#FF7B72",
        "control": "#FF7B72",
        "operator": "#C9D1D9",
        "punctuation": "#C9D1D9",
        
        "class": "#D2A8FF",
        "function": "#D2A8FF",
        "method": "#D2A8FF",
        "variable": "#C9D1D9",
        "parameter": "#C9D1D9",
        "property": "#C9D1D9",
        
        "string": "#A5D6FF",
        "number": "#79C0FF",
        "boolean": "#79C0FF",
        "null": "#79C0FF",
        "constant": "#79C0FF",
        
        "comment": "#8B949E",
        "docstring": "#8B949E",
        "todo": "#FFA657",
        
        "decorator": "#D2A8FF",
        "builtin": "#79C0FF",
        "self": "#C9D1D9",
        "namespace": "#D2A8FF",
        
        "type": "#D2A8FF",
        "type_annotation": "#D2A8FF",
        "interface": "#D2A8FF"
    }    



class BaseHighlighter:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        # Initlaze normal syntax colors
        self.syntax_colors = {
            "keyword": "#569CD6",
            "control": "#C586C0",
            "operator": "#D4D4D4",
            "punctuation": "#D4D4D4",
            "class": "#4EC9B0",
            "function": "#DCDCAA",
            "method": "#DCDCAA",
            "variable": "#9CDCFE",
            "parameter": "#9CDCFE",
            "property": "#9CDCFE",
            "string": "#CE9178",
            "number": "#B5CEA8",
            "boolean": "#569CD6",
            "null": "#569CD6",
            "constant": "#4FC1FF",
            "comment": "#6A9955",
            "docstring": "#6A9955",
            "todo": "#FF8C00",
            "decorator": "#C586C0",
            "builtin": "#4EC9B0",
            "self": "#569CD6",
            "namespace": "#4EC9B0",
            "type": "#4EC9B0",
            "type_annotation": "#4EC9B0",
            "interface": "#4EC9B0"
        }
        
        self.setup_tags()
        self._setup_bindings()
        
        # Highlight delay config
        self._highlight_pending = False
        self._last_change_time = 0
        self._highlight_delay = 50  # Lower delay
        self._last_content = ""     # Add content cache
        
        # Auto pairs
        self.auto_pairs = {
            '"': '"',
            "'": "'",
            '(': ')',
            '[': ']',
            '{': '}',
            '"""': '"""',
            "'''": "'''"
        }
        
        # Basic keyword list
        self.keywords = set(keyword.kwlist)
        self.builtins = set(dir(builtins))
        
        # Languange keywords
        self.language_keywords = {
            'control': {'if', 'else', 'elif', 'while', 'for', 'try', 'except', 'finally', 'with', 'break', 'continue', 'return'},
            'definition': {'def', 'class', 'lambda', 'async', 'await'},
            'module': {'import', 'from', 'as'},
            'value': {'True', 'False', 'None'},
            'context': {'global', 'nonlocal', 'pass', 'yield'}
        }
        
    def setup_tags(self):
        """Configure all syntax highlighting tags"""
        for tag, color in self.syntax_colors.items():
            self.text_widget.tag_configure(tag, foreground=color)
            
    def _setup_bindings(self):
        """Set up event bindings"""
        self.text_widget.bind('<<Modified>>', self._on_text_change)
        self.text_widget.bind('<KeyRelease>', self._on_key_release)
        self.text_widget.bind('(', self._handle_open_parenthesis)  # 绑定左括号
        self.text_widget.bind('<Return>', self._handle_return_key)  # 绑定回车键
        self.text_widget.bind('<Tab>', self._handle_tab_key)  # 绑定Tab键
        
    def _on_text_change(self, event=None):
        """Handle text modification events"""
        if self.text_widget.edit_modified():
            self.text_widget.edit_modified(False)
            self._queue_highlight()
            
    def _on_key_release(self, event=None):
        """Handle key release events"""
        if event.keysym in ('Return', 'BackSpace', 'Delete'):
            self._queue_highlight()
            
    def _queue_highlight(self):
        """Queue highlight task"""
        if not self._highlight_pending:
            self._highlight_pending = True
            self.text_widget.after(self._highlight_delay, self._delayed_highlight)
            
    def _delayed_highlight(self):
        """Execute highlighting with delay"""
        try:
            current_content = self.text_widget.get("1.0", "end-1c")
            # Highlight when content changed
            if current_content != self._last_content:
                self.highlight()
                self._last_content = current_content
        except Exception as e:
            print(f"Highlight failed: {str(e)}")
        finally:
            self._highlight_pending = False
            
    def highlight(self):
        """Perform syntax highlighting"""
        try:
            # Save current status
            current_insert = self.text_widget.index("insert")
            current_view = self.text_widget.yview()
            current_selection = None
            try:
                current_selection = (
                    self.text_widget.index("sel.first"),
                    self.text_widget.index("sel.last")
                )
            except:
                pass
                
            # Highlight
            self._clear_tags()
            text = self.text_widget.get("1.0", "end-1c")
            
            # Process comments and strings
            self._highlight_comments_and_strings(text)
            
            try:
                tree = ast.parse(text)
                self._process_ast(tree)
            except SyntaxError:
                self._basic_highlight(text)
                
            # Backup
            self.text_widget.mark_set("insert", current_insert)
            self.text_widget.yview_moveto(current_view[0])
            if current_selection:
                self.text_widget.tag_add("sel", *current_selection)
                
        except Exception as e:
            print(f"Highlight failed: {str(e)}")
            
    def _basic_highlight(self, text: str):
        """Basic highlighting when syntax errors occur"""
        try:
            import re
            
            # Split words into lines
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Highlight keywords
                for keyword in self.keywords:
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    for match in re.finditer(pattern, line):
                        start = f"{line_num}.{match.start()}"
                        end = f"{line_num}.{match.end()}"
                        self._add_tag("keyword", start, end)
                        
                # Highlight strings
                string_pattern = r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
                for match in re.finditer(string_pattern, line):
                    start = f"{line_num}.{match.start()}"
                    end = f"{line_num}.{match.end()}"
                    self._add_tag("string", start, end)
                    
                # Highlight numbers
                number_pattern = r'\b\d+(\.\d+)?\b'
                for match in re.finditer(number_pattern, line):
                    start = f"{line_num}.{match.start()}"
                    end = f"{line_num}.{match.end()}"
                    self._add_tag("number", start, end)
                    
                # Highlight comments
                comment_pattern = r'#.*$'
                for match in re.finditer(comment_pattern, line):
                    start = f"{line_num}.{match.start()}"
                    end = f"{line_num}.{match.end()}"
                    self._add_tag("comment", start, end)
                    
        except Exception as e:
            print(f"Basic highlight failed: {str(e)}")
            
    def _clear_tags(self):
        """Remove all syntax highlighting tags"""
        try:
            for tag in self.syntax_colors.keys():
                self.text_widget.tag_remove(tag, "1.0", "end")
        except Exception as e:
            print(f"Clear tag error: {str(e)}")
            
    def _add_tag(self, tag: str, start: str, end: str):
        """Add syntax highlighting tag"""
        try:
            self.text_widget.tag_add(tag, start, end)
        except Exception as e:
            print(f"Add tag error - tag: {tag}, start: {start}, end: {end}, err: {str(e)}")

    def get_position(self, node: ast.AST) -> Tuple[str, str]:
        """Get start and end positions of AST node"""
        if hasattr(node, 'lineno'):
            start = f"{node.lineno}.{node.col_offset}"
            end = f"{node.end_lineno}.{node.end_col_offset}" if hasattr(node, 'end_lineno') else f"{node.lineno}.{node.col_offset + len(str(node))}"
            return start, end
        return "1.0", "1.0"

    def _highlight_comments_and_strings(self, text: str):
        """Highlight comments and strings"""
        try:
            # Split content into lines
            lines = text.split('\n')
            current_pos = 0
            
            for line_num, line in enumerate(lines, 1):
                # Process multi comment/string
                triple_quote_pattern = r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')'
                for match in re.finditer(triple_quote_pattern, text[current_pos:]):
                    start_pos = current_pos + match.start()
                    end_pos = current_pos + match.end()
                    
                    # Start row & col
                    start_line = text.count('\n', 0, start_pos) + 1
                    start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
                    
                    # End row & col
                    end_line = text.count('\n', 0, end_pos) + 1
                    end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
                    
                    start = f"{start_line}.{start_col}"
                    end = f"{end_line}.{end_col}"
                    self._add_tag("docstring", start, end)
                
                # Single comment & strings & number & opreator ...
                tokens = list(tokenize.generate_tokens(io.StringIO(line).readline))
                for token in tokens:
                    token_type = token.type
                    token_string = token.string
                    start_col = token.start[1]
                    end_col = token.end[1]
                    
                    if token_type == tokenize.COMMENT:
                        self._add_tag("comment", f"{line_num}.{start_col}", f"{line_num}.{end_col}")
                    elif token_type == tokenize.STRING:
                        if not (token_string.startswith('"""') or token_string.startswith("'''")):
                            self._add_tag("string", f"{line_num}.{start_col}", f"{line_num}.{end_col}")
                    elif token_type == tokenize.NUMBER:
                        self._add_tag("number", f"{line_num}.{start_col}", f"{line_num}.{end_col}")
                    elif token_type == tokenize.OP:
                        self._add_tag("operator", f"{line_num}.{start_col}", f"{line_num}.{end_col}")
                        
                current_pos += len(line) + 1  # +1 for the newline character
                
        except tokenize.TokenError:
            # basic highlight
            self._basic_highlight(text)
        except Exception as e:
            print(f"Comment and strings highlight error: {str(e)}")
            
    def _process_ast(self, tree: ast.AST):
        """Process AST tree"""
        for node in ast.walk(tree):
            self._highlight_node(node)
            
    def _highlight_node(self, node: ast.AST):
        """Highlight specific AST node"""
        if not hasattr(node, 'lineno'):
            return
        
        start, end = self.get_position(node)
        
        # Process different nodes
        if isinstance(node, ast.ClassDef):
            self._highlight_class_def(node, start, end)
        elif isinstance(node, ast.FunctionDef):
            self._highlight_function_def(node, start, end)
        elif isinstance(node, ast.Name):
            self._highlight_name(node, start, end)
        elif isinstance(node, ast.Call):
            self._highlight_call(node)
        elif isinstance(node, ast.Constant):
            self._highlight_constant(node, start, end)
        elif isinstance(node, ast.arg):
            self._highlight_arg(node, start, end)
        elif isinstance(node, ast.AnnAssign):
            self._highlight_annotation(node)
        elif isinstance(node, ast.Import):
            self._highlight_import(node)
        elif isinstance(node, ast.ImportFrom):
            self._highlight_import_from(node)
        elif isinstance(node, ast.Attribute):
            self._highlight_attribute(node)
        elif isinstance(node, ast.Assign):
            self._highlight_assignment(node)
        elif isinstance(node, ast.BinOp):
            self._highlight_operator(node, start, end)
        elif isinstance(node, ast.Compare):
            self._highlight_operator(node, start, end)
        elif isinstance(node, ast.BoolOp):
            self._highlight_operator(node, start, end)
        elif isinstance(node, ast.UnaryOp):
            self._highlight_operator(node, start, end)

    def _highlight_class_def(self, node: ast.ClassDef, start: str, end: str):
        """Highlight class definition"""
        # Class keyword
        keyword_end = f"{node.lineno}.{node.col_offset + 5}"
        self._add_tag("keyword", start, keyword_end)
        
        # Class name
        name_start = f"{node.lineno}.{node.col_offset + 6}"
        name_end = f"{node.lineno}.{node.col_offset + 6 + len(node.name)}"
        self._add_tag("class", name_start, name_end)
        
        # Base class
        for base in node.bases:
            base_start, base_end = self.get_position(base)
            self._add_tag("class", base_start, base_end)

    def _highlight_function_def(self, node: ast.FunctionDef, start: str, end: str):
        """Highlight function definition"""
        # Def keyword
        keyword_end = f"{node.lineno}.{node.col_offset + 3}"
        self._add_tag("keyword", start, keyword_end)
        
        # Name highlight
        name_start = f"{node.lineno}.{node.col_offset + 4}"
        name_end = f"{node.lineno}.{node.col_offset + 4 + len(node.name)}"
        # Check
        if node.name.startswith('__') and node.name.endswith('__'):
            self._add_tag("method", name_start, name_end)
        else:
            self._add_tag("function", name_start, name_end)
        
        # Decorator highlight
        for decorator in node.decorator_list:
            dec_start, dec_end = self.get_position(decorator)
            self._add_tag("decorator", dec_start, dec_end)
        
        # Argument highlight
        for arg in node.args.args:
            arg_start, arg_end = self.get_position(arg)
            self._add_tag("parameter", arg_start, arg_end)

            if arg.annotation:
                ann_start, ann_end = self.get_position(arg.annotation)
                self._add_tag("type_annotation", ann_start, ann_end)

    def _highlight_import(self, node: ast.Import):
        """Highlight import statements"""
        for alias in node.names:
            if hasattr(alias, 'lineno'):
                start = f"{alias.lineno}.{alias.col_offset}"
                end = f"{alias.lineno}.{alias.col_offset + len(alias.name)}"
                self._add_tag("namespace", start, end)
                if alias.asname:
                    as_start = f"{alias.lineno}.{alias.col_offset + len(alias.name) + 4}"
                    as_end = f"{alias.lineno}.{alias.col_offset + len(alias.name) + 4 + len(alias.asname)}"
                    self._add_tag("variable", as_start, as_end)

    def _highlight_import_from(self, node: ast.ImportFrom):
        """Highlight from-import statements"""
        if node.module:
            start = f"{node.lineno}.{node.col_offset + 5}" 
            end = f"{node.lineno}.{node.col_offset + 5 + len(node.module)}"
            self._add_tag("namespace", start, end)
        
        for alias in node.names:
            if hasattr(alias, 'lineno'):
                start = f"{alias.lineno}.{alias.col_offset}"
                end = f"{alias.lineno}.{alias.col_offset + len(alias.name)}"
                self._add_tag("namespace", start, end)
                if alias.asname:
                    as_start = f"{alias.lineno}.{alias.col_offset + len(alias.name) + 4}"
                    as_end = f"{alias.lineno}.{alias.col_offset + len(alias.name) + 4 + len(alias.asname)}"
                    self._add_tag("variable", as_start, as_end)

    def _highlight_attribute(self, node: ast.Attribute):
        """Highlight attribute access"""
        if isinstance(node.value, ast.Name):
            # Highlight attribute access
            start, _ = self.get_position(node.value)
            end = f"{node.value.lineno}.{node.value.col_offset + len(node.value.id)}"
            self._add_tag("variable", start, end)
        
        # Highlight attribles
        attr_start = f"{node.lineno}.{node.col_offset + len(str(node.value)) + 1}"
        attr_end = f"{node.lineno}.{node.col_offset + len(str(node.value)) + 1 + len(node.attr)}"
        self._add_tag("property", attr_start, attr_end)

    def _highlight_name(self, node: ast.Name, start: str, end: str):
        """Highlight name"""
        if node.id in keyword.kwlist:
            self._add_tag("keyword", start, end)
        elif node.id in dir(builtins):
            self._add_tag("builtin", start, end)
        elif node.id.isupper():
            self._add_tag("constant", start, end)
        elif node.id == 'self':
            self._add_tag("self", start, end)
        else:
            self._add_tag("variable", start, end)
            
    def _highlight_call(self, node: ast.Call):
        """Highlight function call"""
        if isinstance(node.func, ast.Name):
            start, end = self.get_position(node.func)
            if node.func.id in dir(builtins):
                self._add_tag("builtin", start, end)
            else:
                self._add_tag("function", start, end)
                
    def _highlight_constant(self, node: ast.Constant, start: str, end: str):
        """Highlight constant"""
        if isinstance(node.value, (int, float)):
            self._add_tag("number", start, end)
        elif isinstance(node.value, str):
            self._add_tag("string", start, end)
            
    def _highlight_arg(self, node: ast.arg, start: str, end: str):
        """Highlight function argument"""
        self._add_tag("parameter", start, end)
        
    def _highlight_annotation(self, node: ast.AnnAssign):
        """Highlight type annotation"""
        if node.annotation:
            start, end = self.get_position(node.annotation)
            self._add_tag("type_annotation", start, end)

    def _highlight_assignment(self, node: ast.Assign):
        """Highlight assignment statement"""
        for target in node.targets:
            start, end = self.get_position(target)
            self._add_tag("variable", start, end)
            
        if isinstance(node.value, ast.Name):
            start, end = self.get_position(node.value)
            self._add_tag("variable", start, end)

    def _handle_open_parenthesis(self, event):
        """Handle parenthesis auto-completion"""
        try:
            current_pos = self.text_widget.index("insert")
            self.text_widget.insert(current_pos, '(')  # Insert left
            self.text_widget.insert(f"{current_pos} + 1c", self.auto_pairs['('])  # Insert right
            self.text_widget.mark_set("insert", f"{current_pos} + 1c")  # Move the curser
            return "break"  
        except Exception as e:
            print(f"Auto completion error: {str(e)}")
        return None

    def _highlight_operator(self, node: ast.AST, start: str, end: str):
        """Highlight operator"""
        self._add_tag("operator", start, end)

    def _handle_return_key(self, event):
        """Handle return key for auto-indentation"""
        try:
            current_line = self.text_widget.get("insert linestart", "insert")
            indent = len(current_line) - len(current_line.lstrip())

            if current_line.rstrip().endswith(":"):
                indent += 4  # Indentation
            self.text_widget.insert("insert", "\n" + " " * indent)
            return "break" 
        except Exception as e:
            print(f"Auto indentation error: {str(e)}")
        return None

    def _handle_tab_key(self, event):
        """Handle tab key to insert 4 spaces"""
        self.text_widget.insert("insert", " " * 4)
        return "break" 

    def set_theme(self, theme_data):
        """Set theme
        
        Args:
            theme_data: Can be theme config dict
        """
        try:
            # Basic properties
            if "base" in theme_data:
                self.text_widget.configure(**theme_data["base"])
                
            # Update colors
            for tag, color in theme_data.items():
                if tag != "base" and isinstance(color, str):
                    self.syntax_colors[tag] = color
                    
            # Setup tags
            self.setup_tags()
            
        except Exception as e:
            print(f"Theme error: {str(e)}")

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)

        self.builtins = set(dir(builtins))
        self.keywords = set(keyword.kwlist)
        
        # Python syntax colors
        self.syntax_colors.update({
            "f_string": self.syntax_colors["string"],     # f-string (use the string color)
            "bytes": self.syntax_colors["string"],        # byte-string
            "exception": self.syntax_colors["class"],     # exception
            "magic_method": self.syntax_colors["function"], # magic method
        })
        self.setup_tags()
        
    def _highlight_node(self, node: ast.AST):
        """Extend base highlighter's node processing"""
        super()._highlight_node(node)
        
        if not hasattr(node, 'lineno'):
            return
            
        start, end = self.get_position(node)
        

        if isinstance(node, ast.JoinedStr):  # f-string
            self._highlight_f_string(node, start, end)
        elif isinstance(node, ast.Bytes):     # byte string
            self._add_tag("bytes", start, end)
        elif isinstance(node, ast.Try):       # try-except block
            self._highlight_try_except(node)
        elif isinstance(node, ast.AsyncFunctionDef):  # async function def
            self._highlight_async_function(node)
            
    def _highlight_f_string(self, node: ast.JoinedStr, start: str, end: str):
        """Highlight f-strings"""
        self._add_tag("f_string", start, end)
        # process f-string
        for value in node.values:
            if isinstance(value, ast.FormattedValue):
                expr_start, expr_end = self.get_position(value)
                self._add_tag("variable", expr_start, expr_end)
                
    def _highlight_try_except(self, node: ast.Try):
        """Highlight try-except blocks"""
        # try-except blocks
        for handler in node.handlers:
            if handler.type:
                start, end = self.get_position(handler.type)
                self._add_tag("exception", start, end)
                
    def _highlight_async_function(self, node: ast.AsyncFunctionDef):
        """Highlight async functions"""
        start, end = self.get_position(node)
        # highlight async keyword
        async_end = f"{node.lineno}.{node.col_offset + 5}"
        self._add_tag("keyword", start, async_end)
        
        # highlight function name
        name_start = f"{node.lineno}.{node.col_offset + 9}"  # async def after
        name_end = f"{node.lineno}.{node.col_offset + 9 + len(node.name)}"
        self._add_tag("function", name_start, name_end)

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

            # Editor tab
            editor_tab = Frame(notebook)
            notebook.add(editor_tab, text="📄 编辑器")

            self.theme_choose = Combobox(editor_tab, values=["Dark", "Light"])
            self.theme_choose.pack(pady=10, padx=0)

            apply_button = Button(editor_tab, text="确认", command=self.apply)
            apply_button.pack(padx=30, pady=10)

            text = Text(editor_tab, font="Consolas")
            text.pack(expand=True)

            self.highlighter = CodeHighlighter(text)
            self.highlighter.highlight()

            text.insert("end", '''"""\nPowered by Phoenix Editor\n"""\n''')
            
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
            third_party_license_button = Button(help_tab, text="第三方协议", command=self.tpl)
            third_party_license_button.pack(pady=10)

            # Start the main loop
            window.mainloop()
        
        except Exception as e:
            showerror("错误", f"程序运行时发生错误: {e} \n\n 请在 Github 提交 issue 反馈，我们会尽快处理。")

    def tpl(self):
        window = Toplevel() 
        window.title("第三方协议")
        window.geometry("500x200")

        # Repo license
        l1 = Label(window, text="[MIT] Phoenix Highlighter(https://github.com/chengzi404-byte/phoenix-highlighter)")
        l1.grid(column=0, row=0)

        # Main loop
        window.mainloop()

    def apply(self):
        if self.theme_choose.get() == "Dark":
            self.highlighter.set_theme(Theme.Dark)
        elif self.theme_choose.get() == "Light":
            self.highlighter.set_theme(Theme.Light)
        self.highlighter.highlight()

if __name__ == "__main__":
    package = Package()
    package.main()
