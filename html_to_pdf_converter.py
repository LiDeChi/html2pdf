import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import pdfkit
import json

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'last_input_path': '',
        'last_output_path': '',
        'wkhtmltopdf_path': '/usr/local/bin/wkhtmltopdf'
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def select_input_folder():
    config = load_config()
    initial_dir = config.get('last_input_path') or '/'
    folder_path = filedialog.askdirectory(initialdir=initial_dir)
    if folder_path:
        input_folder_var.set(folder_path)
        config['last_input_path'] = folder_path
        save_config(config)

def select_output_folder():
    config = load_config()
    initial_dir = config.get('last_output_path') or '/'
    folder_path = filedialog.askdirectory(initialdir=initial_dir)
    if folder_path:
        output_folder_var.set(folder_path)
        config['last_output_path'] = folder_path
        save_config(config)

def select_wkhtmltopdf():
    config = load_config()
    initial_dir = os.path.dirname(config.get('wkhtmltopdf_path') or '/')
    wkhtmltopdf_path = filedialog.askopenfilename(title="选择wkhtmltopdf可执行文件", initialdir=initial_dir)
    if wkhtmltopdf_path:
        wkhtmltopdf_path_var.set(wkhtmltopdf_path)
        config['wkhtmltopdf_path'] = wkhtmltopdf_path
        save_config(config)

def convert_to_pdf():
    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()
    wkhtmltopdf_path = wkhtmltopdf_path_var.get()
    
    if not input_folder or not output_folder:
        messagebox.showerror("错误", "请选择输入和输出文件夹")
        return
    
    if not wkhtmltopdf_path:
        messagebox.showerror("错误", "请选择wkhtmltopdf可执行文件")
        return

    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    options = {
        'load-error-handling': 'ignore',
        'load-media-error-handling': 'ignore',
        'no-stop-slow-scripts': True,
        'enable-local-file-access': True
    }

    for article_folder in Path(input_folder).iterdir():
        if article_folder.is_dir():
            html_file = next(article_folder.glob('*.html'), None)
            if html_file:
                pdf_file = Path(output_folder) / f"{article_folder.name}.pdf"
                try:
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    base_url = article_folder.absolute().as_uri()
                    html_content = html_content.replace('src="', f'src="{base_url}/')
                    html_content = html_content.replace('href="', f'href="{base_url}/')

                    pdfkit.from_string(html_content, str(pdf_file), configuration=config, options=options, verbose=True)
                    print(f"已转换: {pdf_file}")
                except Exception as e:
                    print(f"转换失败 {html_file}: {str(e)}")

    messagebox.showinfo("完成", "所有HTML文件已转换为PDF")

# 创建主窗口
root = tk.Tk()
root.title("HTML到PDF转换器")
root.geometry("650x450")

# 使用ttk.Style来设置主题
style = ttk.Style()
style.theme_use('default')

# 设置颜色
style.configure('TFrame', background='#F0F0F0')
style.configure('TLabelframe', background='#F0F0F0')
style.configure('TLabelframe.Label', background='#F0F0F0', foreground='#333333', font=('Arial', 10, 'bold'))
style.configure('TButton', background='#4CAF50', foreground='white', font=('Arial', 10, 'bold'))
style.map('TButton', background=[('active', '#45a049')])
style.configure('TLabel', background='#F0F0F0', foreground='#333333', font=('Arial', 10))
style.configure('TEntry', fieldbackground='white')

# 创建主框架
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# 创建并放置组件
input_folder_var = tk.StringVar()
output_folder_var = tk.StringVar()
wkhtmltopdf_path_var = tk.StringVar()

# 输入文件夹选择
input_frame = ttk.LabelFrame(main_frame, text="输入设置", padding="10")
input_frame.pack(fill=tk.X, pady=10)

ttk.Label(input_frame, text="输入文件夹:").pack(side=tk.LEFT, padx=5)
ttk.Entry(input_frame, textvariable=input_folder_var, width=50).pack(side=tk.LEFT, padx=5)
ttk.Button(input_frame, text="选择", command=select_input_folder).pack(side=tk.LEFT, padx=5)

# 输出文件夹选择
output_frame = ttk.LabelFrame(main_frame, text="输出设置", padding="10")
output_frame.pack(fill=tk.X, pady=10)

ttk.Label(output_frame, text="输出文件夹:").pack(side=tk.LEFT, padx=5)
ttk.Entry(output_frame, textvariable=output_folder_var, width=50).pack(side=tk.LEFT, padx=5)
ttk.Button(output_frame, text="选择", command=select_output_folder).pack(side=tk.LEFT, padx=5)

# wkhtmltopdf路径选择
wkhtmltopdf_frame = ttk.LabelFrame(main_frame, text="wkhtmltopdf设置", padding="10")
wkhtmltopdf_frame.pack(fill=tk.X, pady=10)

ttk.Label(wkhtmltopdf_frame, text="wkhtmltopdf路径:").pack(side=tk.LEFT, padx=5)
ttk.Entry(wkhtmltopdf_frame, textvariable=wkhtmltopdf_path_var, width=50).pack(side=tk.LEFT, padx=5)
ttk.Button(wkhtmltopdf_frame, text="选择", command=select_wkhtmltopdf).pack(side=tk.LEFT, padx=5)

# 转换按钮
convert_button = ttk.Button(main_frame, text="转换为PDF", command=convert_to_pdf)
convert_button.pack(pady=20)

# 加载配置
config = load_config()
input_folder_var.set(config.get('last_input_path', ''))
output_folder_var.set(config.get('last_output_path', ''))
wkhtmltopdf_path_var.set(config.get('wkhtmltopdf_path', '/usr/local/bin/wkhtmltopdf'))

# 运行主循环
root.mainloop()
