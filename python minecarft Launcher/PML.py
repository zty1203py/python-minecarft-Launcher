import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import os
import subprocess
import shutil


class MinecraftLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Launcher")
        self.root.geometry("600x400")

        # 设置主题颜色
        self.root.configure(bg="#2c3e50")  # 深蓝灰色背景

        # 设置样式
        style = ttk.Style()
        style.theme_use("clam")  # 使用clam主题
        style.configure("TLabel", foreground="white", background="#2c3e50", font=("Arial", 12))
        style.configure("TButton", foreground="white", background="#2980b9", font=("Arial", 12), padding=10)
        style.configure("TEntry", foreground="black", font=("Arial", 12))
        style.configure("TCombobox", font=("Arial", 12))

        # 界面布局
        self.username = tk.StringVar(value="Player")
        self.version = tk.StringVar()
        self.game_directory = tk.StringVar(value=os.path.join(os.path.expanduser("~"), ".minecraft"))
        self.selected_mod = tk.StringVar()
        self.selected_skin = tk.StringVar()
        self.server_address = tk.StringVar()

        # 布局容器
        main_frame = ttk.Frame(self.root, padding="20", relief="raised", style="TFrame")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # 用户名
        ttk.Label(main_frame, text="用户名:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        ttk.Entry(main_frame, textvariable=self.username, width=25).grid(row=0, column=1, padx=10, pady=10)

        # 版本选择
        ttk.Label(main_frame, text="选择版本:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.version_combobox = ttk.Combobox(main_frame, textvariable=self.version, width=23)
        self.version_combobox.grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(main_frame, text="获取版本列表", command=self.fetch_versions).grid(row=1, column=2, padx=10, pady=10)

        # 游戏目录
        ttk.Label(main_frame, text="游戏目录:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        ttk.Entry(main_frame, textvariable=self.game_directory, width=25).grid(row=2, column=1, padx=10, pady=10)
        ttk.Button(main_frame, text="选择目录", command=self.select_directory).grid(row=2, column=2, padx=10, pady=10)

        # MOD管理
        ttk.Label(main_frame, text="管理MOD:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        ttk.Button(main_frame, text="添加MOD", command=self.add_mod).grid(row=3, column=1, padx=10, pady=10, sticky="w")
        ttk.Button(main_frame, text="显示MOD列表", command=self.show_mods).grid(row=3, column=2, padx=10, pady=10)

        # 皮肤管理
        ttk.Label(main_frame, text="皮肤管理:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        ttk.Button(main_frame, text="选择皮肤", command=self.select_skin).grid(row=4, column=1, padx=10, pady=10,
                                                                               sticky="w")
        ttk.Button(main_frame, text="应用皮肤", command=self.apply_skin).grid(row=4, column=2, padx=10, pady=10)

        # 服务器地址
        ttk.Label(main_frame, text="服务器地址:").grid(row=5, column=0, padx=10, pady=10, sticky="e")
        ttk.Entry(main_frame, textvariable=self.server_address, width=25).grid(row=5, column=1, padx=10, pady=10)
        ttk.Button(main_frame, text="选择服务器", command=self.select_server).grid(row=5, column=2, padx=10, pady=10)

        # 下载与启动按钮
        ttk.Button(main_frame, text="下载游戏文件", command=self.download_version).grid(row=6, columnspan=3, pady=20)
        ttk.Button(main_frame, text="启动游戏", command=self.launch_game).grid(row=7, columnspan=3, pady=10)

    def select_directory(self):
        directory = filedialog.askdirectory(title="选择游戏目录")
        if directory:
            self.game_directory.set(directory)

    def fetch_versions(self):
        try:
            response = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json")
            response.raise_for_status()
            version_data = response.json()
            self.versions = [v['id'] for v in version_data['versions']]
            self.version_combobox['values'] = self.versions
            messagebox.showinfo("信息", "版本列表获取成功。")
        except Exception as e:
            messagebox.showerror("错误", f"获取版本列表失败：{e}")

    def download_version(self):
        selected_version = self.version.get()
        game_dir = self.game_directory.get()

        if not selected_version or not game_dir:
            messagebox.showerror("错误", "请先选择版本和游戏目录。")
            return

        try:
            response = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json")
            response.raise_for_status()
            version_data = response.json()
            version_info = next((v for v in version_data['versions'] if v['id'] == selected_version), None)

            if not version_info:
                messagebox.showerror("错误", "未找到指定版本。")
                return

            version_url = version_info['url']
            version_response = requests.get(version_url)
            version_response.raise_for_status()
            version_details = version_response.json()

            jar_url = version_details['downloads']['client']['url']
            jar_path = os.path.join(game_dir, f"versions/{selected_version}/{selected_version}.jar")
            os.makedirs(os.path.dirname(jar_path), exist_ok=True)

            with requests.get(jar_url, stream=True) as jar_response:
                jar_response.raise_for_status()
                with open(jar_path, 'wb') as jar_file:
                    for chunk in jar_response.iter_content(chunk_size=8192):
                        jar_file.write(chunk)

            messagebox.showinfo("信息", f"版本 {selected_version} 下载成功。")
        except Exception as e:
            messagebox.showerror("错误", f"下载版本失败：{e}")

    def add_mod(self):
        mod_file = filedialog.askopenfilename(title="选择MOD文件",
                                              filetypes=[("Jar files", "*.jar"), ("Zip files", "*.zip")])
        if mod_file:
            mods_dir = os.path.join(self.game_directory.get(), "mods")
            os.makedirs(mods_dir, exist_ok=True)
            shutil.copy(mod_file, mods_dir)
            messagebox.showinfo("信息", "MOD添加成功。")

    def show_mods(self):
        mods_dir = os.path.join(self.game_directory.get(), "mods")
        if not os.path.exists(mods_dir):
            messagebox.showinfo("信息", "当前没有安装MOD。")
            return

        mods_list = os.listdir(mods_dir)
        if mods_list:
            messagebox.showinfo("已安装的MOD", "\n".join(mods_list))
        else:
            messagebox.showinfo("信息", "当前没有安装MOD。")

    def select_skin(self):
        skin_file = filedialog.askopenfilename(title="选择皮肤文件", filetypes=[("PNG files", "*.png")])
        if skin_file:
            self.selected_skin.set(skin_file)
            messagebox.showinfo("信息", "皮肤选择成功。")

    def apply_skin(self):
        skin_file = self.selected_skin.get()
        if not skin_file:
            messagebox.showerror("错误", "请先选择皮肤。")
            return

        game_dir = self.game_directory.get()
        skin_dir = os.path.join(game_dir, "skins")
        os.makedirs(skin_dir, exist_ok=True)
        shutil.copy(skin_file, os.path.join(skin_dir, "custom_skin.png"))
        messagebox.showinfo("信息", "皮肤已应用。")

    def select_server(self):
        predefined_servers = {
            "Hypixel": "mc.hypixel.net",
            "Mineplex": "us.mineplex.com",
            "CubeCraft": "play.cubecraft.net"
        }

        selected_server = tk.StringVar()
        server_window = tk.Toplevel(self.root)
        server_window.title("选择服务器")

        for server_name, server_address in predefined_servers.items():
            ttk.Radiobutton(server_window, text=server_name, variable=selected_server, value=server_address).pack(
                anchor="w")

        def set_server():
            self.server_address.set(selected_server.get())
            server_window.destroy()

        ttk.Button(server_window, text="选择", command=set_server).pack()

    def launch_game(self):
        game_dir = self.game_directory.get()
        selected_version = self.version.get()
        username = self.username.get()
        server_address = self.server_address.get()

        if not selected_version or not game_dir or not username:
            messagebox.showerror("错误", "请填写所有必要信息。")
            return

        # 模拟启动游戏
        messagebox.showinfo("信息", f"正在启动游戏: {selected_version}\n用户名: {username}\n服务器: {server_address}")

        # 在此处，您可以使用subprocess调用实际的Minecraft启动器，例如：
        # subprocess.run(["java", "-jar", "MinecraftLauncher.jar", "--version", selected_version, "--username", username])


if __name__ == "__main__":
    root = tk.Tk()
    launcher = MinecraftLauncher(root)
    root.mainloop()