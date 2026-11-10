import tkinter as tk
from tkinter import ttk
import psutil
import platform
import cpuinfo
import threading
import time

LANGUAGES = {
    "vi": {
        "tab_cpu": " CPU ",
        "tab_ram": " Bộ nhớ (RAM) ",
        "tab_disk": " Lưu trữ ",
        "cpu_name": "Tên bộ vi xử lý (Processor):",
        "cpu_cores": "Số nhân vật lý (Cores):",
        "cpu_threads": "Số luồng logic (Threads):",
        "os_info": "Hệ điều hành máy tính:",
        "cpu_live": "Mức độ sử dụng CPU hiện tại:",
        "ram_total": "Tổng dung lượng RAM phần cứng:",
        "ram_used": "Bộ nhớ RAM đang sử dụng:",
        "ram_free": "Bộ nhớ RAM còn trống khả dụng:",
        "ram_percent": "Tỷ lệ tiêu thụ RAM hiện tại:",
        "disk_device": "Ổ đĩa",
        "disk_free": "Dung lượng trống"
    },
    "en": {
        "tab_cpu": " CPU ",
        "tab_ram": " Memory (RAM) ",
        "tab_disk": " Storage ",
        "cpu_name": "Processor Name:",
        "cpu_cores": "Physical Cores:",
        "cpu_threads": "Logical Threads:",
        "os_info": "Operating System:",
        "cpu_live": "Current CPU Usage:",
        "ram_total": "Total Hardware RAM:",
        "ram_used": "Used RAM Memory:",
        "ram_free": "Available Free RAM:",
        "ram_percent": "Current RAM Usage Rate:",
        "disk_device": "Drive",
        "disk_free": "Free Space"
    }
}

current_lang = "vi"
current_cpu_percent = 0.0  # Biến lưu trữ phần trăm CPU chạy thực tế

# Hàm chạy luồng ngầm chuyên dụng đo % CPU chuẩn xác
def luong_do_cpu_chinh_xac():
    global current_cpu_percent
    while True:
        # psutil đo chính xác nhất khi có khoảng thời gian nghỉ nhỏ (0.5 giây đến 1 giây)
        current_cpu_percent = psutil.cpu_percent(interval=0.5)
        time.sleep(0.1)

# Khởi động luồng ngầm ngay lập tức
thread_cpu = threading.Thread(target=luong_do_cpu_chinh_xac, daemon=True)
thread_cpu.start()

def get_cpu_info():
    try:
        info = cpuinfo.get_cpu_info()
        if 'brand_raw' in info:
            return info['brand_raw'].strip()
    except:
        pass
    return platform.processor()

def switch_language(event=None):
    global current_lang
    selection = lang_combo.get()
    
    if selection == "Tiếng Việt":
        current_lang = "vi"
    else:
        current_lang = "en"
        
    lang_data = LANGUAGES[current_lang]
    
    notebook.tab(tab1, text=lang_data["tab_cpu"])
    notebook.tab(tab2, text=lang_data["tab_ram"])
    notebook.tab(tab3, text=lang_data["tab_disk"])
    
    lbl_title_cpu.config(text=lang_data["cpu_name"])
    lbl_title_cores.config(text=lang_data["cpu_cores"])
    lbl_title_threads.config(text=lang_data["cpu_threads"])
    lbl_title_os.config(text=lang_data["os_info"])
    lbl_live_label.config(text=lang_data["cpu_live"])
    
    lbl_title_total.config(text=lang_data["ram_total"])
    lbl_title_used.config(text=lang_data["ram_used"])
    lbl_title_free.config(text=lang_data["ram_free"])
    lbl_title_percent.config(text=lang_data["ram_percent"])
    
    quet_o_cung()

# Hàm cập nhật giao diện liên tục mỗi 1 giây (Đọc số liệu từ luồng nền)
def cap_nhat_lien_tuc():
    try:
        # 1. Đo phần trăm CPU thời gian thực từ biến dùng chung của luồng ngầm
        lbl_live_cpu_use.config(text=f"{current_cpu_percent} %")
        progress_cpu['value'] = current_cpu_percent
        
        # 2. Cập nhật thông số RAM
        ram = psutil.virtual_memory()
        lbl_ram_used.config(text=f"{round(ram.used / (1024**3), 2)} GB")
        lbl_ram_free.config(text=f"{round(ram.available / (1024**3), 2)} GB")
        lbl_ram_percent.config(text=f"{ram.percent} %")
        progress_ram['value'] = ram.percent
    except:
        pass
    root.after(1000, cap_nhat_lien_tuc)

def quet_o_cung():
    for widget in tab3.winfo_children():
        widget.destroy()
        
    lang_data = LANGUAGES[current_lang]
    for partition in psutil.disk_partitions():
        try:
            if 'cdrom' in partition.opts or partition.fstype == '':
                continue
            usage = psutil.disk_usage(partition.mountpoint)
            
            disk_row = tk.Frame(tab3, bg="#1e293b", pady=5)
            disk_row.pack(fill="x", padx=15)
            
            lbl_name = tk.Label(disk_row, text=f"{lang_data['disk_device']} {partition.device} ({partition.fstype})", font=("Arial", 10, "bold"), fg="#38bdf8", bg="#1e293b")
            lbl_name.pack(anchor="w")
            
            lbl_detail = tk.Label(disk_row, text=f"{lang_data['disk_free']}: {round(usage.free / (1024**3), 1)} GB / Total: {round(usage.total / (1024**3), 1)} GB", font=("Arial", 10), fg="#f8fafc", bg="#1e293b")
            lbl_detail.pack(anchor="w", pady=(0, 2))
            
            p_disk = ttk.Progressbar(disk_row, mode='determinate', style="TProgressbar")
            p_disk.pack(fill="x")
            p_disk['value'] = usage.percent
        except:
            continue

# --- KHỞI TẠO CỬA SỔ CHÍNH ---
root = tk.Tk()
root.title("cpuchecker")
root.geometry("480x430")
root.configure(bg="#0f172a")

top_bar = tk.Frame(root, bg="#0f172a")
top_bar.pack(fill="x", padx=10, pady=(5, 0))
lang_label = tk.Label(top_bar, text="Language:", fg="#94a3b8", bg="#0f172a", font=("Arial", 9))
lang_label.pack(side="left", padx=5)
lang_combo = ttk.Combobox(top_bar, values=["Tiếng Việt", "English"], width=12, state="readonly")
lang_combo.set("Tiếng Việt")
lang_combo.pack(side="left")
lang_combo.bind("<<ComboboxSelected>>", switch_language)

style = ttk.Style()
style.theme_use('default')
style.configure('TNotebook', background='#0f172a', borderwidth=0)
style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'), padding=5, background='#1e293b', foreground='#94a3b8')
style.map('TNotebook.Tab', background=[('selected', '#0284c7')], foreground=[('selected', '#ffffff')])
style.configure("TProgressbar", thickness=12, foreground='#38bdf8', background='#38bdf8')

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

tab1 = tk.Frame(notebook, bg="#1e293b")
tab2 = tk.Frame(notebook, bg="#1e293b")
tab3 = tk.Frame(notebook, bg="#1e293b")

notebook.add(tab1, text=" CPU ")
notebook.add(tab2, text=" Memory (RAM) ")
notebook.add(tab3, text=" Storage ")

def ghep_dong(parent, row_num):
    lbl_t = tk.Label(parent, text="", font=("Arial", 10, "bold"), fg="#38bdf8", bg="#1e293b", anchor="w")
    lbl_t.grid(row=row_num, column=0, sticky="w", pady=6)
    lbl_v = tk.Label(parent, text="", font=("Arial", 10), fg="#f8fafc", bg="#1e293b", anchor="w")
    lbl_v.grid(row=row_num, column=1, sticky="w", pady=6, padx=10)
    return lbl_t, lbl_v

# Tạo Tab CPU
grid_cpu = tk.Frame(tab1, bg="#1e293b", pady=15, padx=15)
grid_cpu.pack(fill="both", expand=True)
lbl_title_cpu, lbl_cpu_name = ghep_dong(grid_cpu, 0)
lbl_title_cores, lbl_cpu_cores = ghep_dong(grid_cpu, 1)
lbl_title_threads, lbl_cpu_threads = ghep_dong(grid_cpu, 2)
lbl_title_os, lbl_os_info = ghep_dong(grid_cpu, 3)

lbl_live_label = tk.Label(tab1, text="", font=("Arial", 10, "bold"), fg="#38bdf8", bg="#1e293b")
lbl_live_label.pack(anchor="w", padx=15)
lbl_live_cpu_use = tk.Label(tab1, text="0 %", font=("Arial", 12, "bold"), fg="#38bdf8", bg="#1e293b")
lbl_live_cpu_use.pack(anchor="w", padx=15)
progress_cpu = ttk.Progressbar(tab1, mode='determinate', style="TProgressbar")
progress_cpu.pack(fill="x", padx=15, pady=(2, 20))

# Tạo Tab RAM
grid_ram = tk.Frame(tab2, bg="#1e293b", pady=15, padx=15)
grid_ram.pack(fill="both", expand=True)
lbl_title_total, lbl_ram_total = ghep_dong(grid_ram, 0)
lbl_title_used, lbl_ram_used = ghep_dong(grid_ram, 1)
lbl_title_free, lbl_ram_free = ghep_dong(grid_ram, 2)
lbl_title_percent, lbl_ram_percent = ghep_dong(grid_ram, 3)

progress_ram = ttk.Progressbar(tab2, mode='determinate', style="TProgressbar")
progress_ram.pack(fill="x", padx=15, pady=(0, 20))

# --- NẠP DỮ LIỆU BAN ĐẦU ---
ram_init = psutil.virtual_memory()
lbl_cpu_name.config(text=get_cpu_info())
lbl_cpu_cores.config(text=f"{psutil.cpu_count(logical=False)}")
lbl_cpu_threads.config(text=f"{psutil.cpu_count(logical=True)}")
lbl_os_info.config(text=f"{platform.system()} {platform.release()} ({platform.machine()})")
lbl_ram_total.config(text=f"{round(ram_init.total / (1024**3), 2)} GB")

switch_language()
cap_nhat_lien_tuc()
root.mainloop()
