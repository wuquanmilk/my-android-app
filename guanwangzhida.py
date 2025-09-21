import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import json
import os
import re
import sys
import shutil
from datetime import datetime

class WebLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("智能官网直达工具")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        self.root.minsize(800, 600)  # 设置最小窗口尺寸
        
        # 跨平台数据文件路径
        app_data_path = os.path.join(os.path.expanduser("~"), ".weblauncher")
        self.data_file = os.path.join(app_data_path, "custom_sites.json")
        os.makedirs(app_data_path, exist_ok=True)
        
        # 检查旧路径并迁移数据
        self.migrate_old_data()
        
        # 加载网站数据
        self.websites = self.load_websites()
        self.current_filter = "全部"
        
        # 创建界面组件
        self.create_widgets()
    
    def migrate_old_data(self):
        """迁移旧版本数据"""
        # macOS 旧路径
        old_mac_path = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "WebLauncher", "custom_sites.json")
        
        # Windows 旧路径
        old_win_path = os.path.join(os.getenv('APPDATA'), "WebLauncher", "custom_sites.json")
        
        # Linux 旧路径
        old_linux_path = os.path.join(os.path.expanduser("~"), ".config", "WebLauncher", "custom_sites.json")
        
        old_paths = [old_mac_path, old_win_path, old_linux_path]
        
        for old_path in old_paths:
            if os.path.exists(old_path) and not os.path.exists(self.data_file):
                try:
                    shutil.copy2(old_path, self.data_file)
                    print(f"迁移旧数据: {old_path} -> {self.data_file}")
                except Exception as e:
                    print(f"数据迁移失败: {str(e)}")
    
    def create_widgets(self):
        # 主框架 - 使用PanedWindow实现可调整大小的区域
        self.main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=4)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧面板（网站展示区）
        left_frame = ttk.Frame(self.main_paned, padding=5)
        self.main_paned.add(left_frame, stretch="always")
        
        # 右侧面板（添加网站区）
        right_frame = ttk.Frame(self.main_paned, padding=10, width=300)
        self.main_paned.add(right_frame, stretch="never")
        
        # 左侧面板内容
        # 标题栏
        title_frame = ttk.Frame(left_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(title_frame, text="智能官网直达工具", 
                 font=("Helvetica", 18, "bold"), 
                 foreground="#2c3e50").pack()
        
        # 搜索框
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(search_frame, text="搜索网站:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="搜索", 
                  command=self.search_website).pack(side=tk.LEFT)
        ttk.Button(search_frame, text="重置", 
                  command=self.reset_search).pack(side=tk.LEFT, padx=5)
        
        # 网站分类导航 - 动态生成
        nav_frame = ttk.LabelFrame(left_frame, text="分类导航", padding=10)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 获取所有存在的分类（包括默认和用户添加的）
        all_categories = set()  # 不再默认包含"全部"
        for site in self.websites:
            all_categories.add(site["category"])
        
        # 按字母顺序排序
        sorted_categories = sorted(all_categories)
        
        # 创建水平滚动条和Canvas
        nav_scroll_frame = ttk.Frame(nav_frame)
        nav_scroll_frame.pack(fill=tk.X, expand=True)
        
        nav_canvas = tk.Canvas(nav_scroll_frame, height=40, highlightthickness=0)
        nav_scrollbar = ttk.Scrollbar(nav_scroll_frame, orient=tk.HORIZONTAL, command=nav_canvas.xview)
        nav_canvas.configure(xscrollcommand=nav_scrollbar.set)
        
        nav_canvas.pack(side=tk.TOP, fill=tk.X, expand=True)
        nav_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建按钮容器框架
        nav_buttons_frame = ttk.Frame(nav_canvas)
        nav_canvas.create_window((0, 0), window=nav_buttons_frame, anchor="nw")
        
        # 配置Canvas的滚动区域
        def on_frame_configure(event):
            nav_canvas.configure(scrollregion=nav_canvas.bbox("all"))
        
        nav_buttons_frame.bind("<Configure>", on_frame_configure)
        
        # 创建自定义按钮样式
        self.style = ttk.Style()
        self.style.configure("Red.TButton", foreground="red")
        
        self.nav_buttons = []
        # 首先创建"我的"按钮（红色）
        btn_my = ttk.Button(nav_buttons_frame, text="我的",
                           command=lambda c="我的": self.filter_sites(c),
                           width=10, padding=4, style="Red.TButton")
        btn_my.pack(side=tk.LEFT, padx=4, pady=2)
        self.nav_buttons.append(btn_my)
        
        # 然后创建"全部"按钮
        btn_all = ttk.Button(nav_buttons_frame, text="全部",
                           command=lambda c="全部": self.filter_sites(c),
                           width=10, padding=4)
        btn_all.pack(side=tk.LEFT, padx=4, pady=2)
        self.nav_buttons.append(btn_all)
        
        # 最后按字母顺序创建其他分类按钮
        for cat in sorted_categories:
            if cat not in ["我的", "全部"]:  # 跳过已经添加的分类
                btn = ttk.Button(nav_buttons_frame, text=cat,
                               command=lambda c=cat: self.filter_sites(c),
                               width=10, padding=4)
                btn.pack(side=tk.LEFT, padx=4, pady=2)
                self.nav_buttons.append(btn)
        
        # 按钮展示区
        sites_frame = ttk.LabelFrame(left_frame, text="网站列表", padding=10)
        sites_frame.pack(fill=tk.BOTH, expand=True)
        
        # 使用Canvas实现滚动
        self.canvas = tk.Canvas(sites_frame, bg="#ffffff", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(sites_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        
        # 添加网站面板（右侧面板）
        self.input_frame = ttk.LabelFrame(right_frame, text="添加新网站", padding=15)
        self.input_frame.pack(fill=tk.BOTH)
        self.create_input_fields()
        
        # 状态栏
        self.status = ttk.Label(self.root, text="就绪", 
                              relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 初始加载
        self.populate_buttons()
        
        # 绑定事件
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
    def _on_mousewheel(self, event):
        """支持鼠标滚轮滚动"""
        if sys.platform == "darwin":
            self.canvas.yview_scroll(-1 * event.delta, "units")
        else:
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
    def _on_canvas_configure(self, event):
        """调整滚动区域宽度"""
        self.canvas.itemconfig("all", width=event.width)
        
    def create_input_fields(self):
        # 使用网格布局组织输入字段
        # 网站名称输入
        ttk.Label(self.input_frame, text="名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(self.input_frame, width=25)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 网站URL输入
        ttk.Label(self.input_frame, text="URL:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.url_entry = ttk.Entry(self.input_frame, width=35)
        self.url_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 分类选择 - 动态生成
        ttk.Label(self.input_frame, text="分类:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.category = tk.StringVar(value="其他")
        
        # 获取所有存在的分类（去除"全部"）
        all_categories = set()
        for site in self.websites:
            all_categories.add(site["category"])
        
        # 按字母顺序排序
        sorted_categories = sorted(all_categories)
        
        # 添加默认选项（如果不存在）
        if "其他" not in sorted_categories:
            sorted_categories.append("其他")
        
        category_menu = ttk.OptionMenu(self.input_frame, self.category, "其他", *sorted_categories)
        category_menu.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 添加按钮
        add_btn_frame = ttk.Frame(self.input_frame)
        add_btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        add_btn = ttk.Button(add_btn_frame, text="添加网站", 
                           command=self.add_website, width=20)
        add_btn.pack()
        
    def load_websites(self):
        """加载已保存的网站数据"""
        # 扩展的默认网站列表
        default_sites = [
            # 社交
            {"id": "social_1", "name": "微博", "url": "https://weibo.com", "category": "社交"},
            {"id": "social_2", "name": "微信", "url": "https://wx.qq.com", "category": "社交"},
            {"id": "social_3", "name": "QQ", "url": "https://im.qq.com", "category": "社交"},
            {"id": "social_4", "name": "知乎", "url": "https://www.zhihu.com", "category": "社交"},
            {"id": "social_5", "name": "豆瓣", "url": "https://www.douban.com", "category": "社交"},
            
            # 工具
            {"id": "tools_1", "name": "GitHub", "url": "https://github.com", "category": "工具"},
            {"id": "tools_2", "name": "百度网盘", "url": "https://pan.baidu.com", "category": "工具"},
            {"id": "tools_3", "name": "阿里云", "url": "https://www.aliyun.com", "category": "工具"},
            {"id": "tools_4", "name": "CSDN", "url": "https://www.csdn.net", "category": "工具"},
            {"id": "tools_5", "name": "Stack Overflow", "url": "https://stackoverflow.com", "category": "工具"},
            
            # 购物
            {"id": "shopping_1", "name": "淘宝", "url": "https://www.taobao.com", "category": "购物"},
            {"id": "shopping_2", "name": "京东", "url": "https://www.jd.com", "category": "购物"},
            {"id": "shopping_3", "name": "拼多多", "url": "https://www.pinduoduo.com", "category": "购物"},
            {"id": "shopping_4", "name": "唯品会", "url": "https://www.vip.com", "category": "购物"},
            {"id": "shopping_5", "name": "网易严选", "url": "https://you.163.com", "category": "购物"},
            
            # 新闻
            {"id": "news_1", "name": "新浪新闻", "url": "https://news.sina.com.cn", "category": "新闻"},
            {"id": "news_2", "name": "腾讯新闻", "url": "https://news.qq.com", "category": "新闻"},
            {"id": "news_3", "name": "人民日报", "url": "https://www.people.com.cn", "category": "新闻"},
            {"id": "news_4", "name": "36氪氪", "url": "https://36kr.com", "category": "新闻"},
            {"id": "news_5", "name": "虎嗅", "url": "https://www.huxiu.com", "category": "新闻"},
            
            # 视频
            {"id": "video_1", "name": "哔哔哩哔哔哩", "url": "https://www.bilibili.com", "category": "视频"},
            {"id": "video_2", "name": "腾讯视频", "url": "https://v.qq.com", "category": "视频"},
            {"id": "video_3", "name": "爱奇艺", "url": "https://www.iqiyi.com", "category": "视频"},
            {"id": "video_4", "name": "优酷", "url": "https://www.youku.com", "category": "视频"},
            {"id": "video_5", "name": "芒果TV", "url": "https://www.mgtv.com", "category": "视频"},
            
            # 其他
            {"id": "other_1", "name": "知乎日报", "url": "https://daily.zhihu.com", "category": "其他"},
            {"id": "other_2", "name": "中国大学MOOC", "url": "https://www.icourse163.org", "category": "其他"},
            {"id": "other_3", "name": "W3School", "url": "https://www.w3school.com.cn", "category": "其他"},
            {"id": "other_4", "name": "LeetCode", "url": "https://leetcode.cn", "category": "其他"},
            {"id": "other_5", "name": "斗鱼直播", "url": "https://www.douyu.com", "category": "其他"},
            {"id": "other_6", "name": "虎牙直播", "url": "https://www.huya.com", "category": "其他"},
        ]
        
        if not os.path.exists(self.data_file):
            # 创建默认数据文件
            try:
                with open(self.data_file, "w", encoding="utf-8") as f:
                    for site in default_sites:
                        f.write(json.dumps(site, ensure_ascii=False) + "\n")
                return default_sites
            except Exception as e:
                messagebox.showerror("错误", f"创建默认数据失败: {str(e)}")
                return default_sites[:1]  # 返回至少一个网站
        
        sites = []
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        site = json.loads(line)
                        if self.validate_site(site):
                            sites.append(site)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            messagebox.showerror("错误", f"加载数据失败: {str(e)}")
            return default_sites
        
        # 如果文件存在但为空，添加默认网站
        if not sites:
            return default_sites
        
        return sites
    
    def validate_site(self, site):
        """验证网站数据有效性"""
        return ("name" in site and "url" in site and 
                isinstance(site["name"], str) and 
                isinstance(site["url"], str) and
                self.is_valid_url(site["url"]))
    
    def is_valid_url(self, url):
        """增强型URL验证（更宽松）"""
        regex = re.compile(
            r'^(https?://)?'  # 协议可选
            r'([A-Za-z0-9-]+\.)+[A-Za-z]{2,}'  # 域名部分
            r'(:\d+)?'  # 端口
            r'(/[/\w\.-]*)*$', re.IGNORECASE)
        return re.match(regex, url) is not None
    
    def add_website(self):
        """添加新网站"""
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()
        category = self.category.get()
        
        if not name or not url:
            messagebox.showerror("错误", "名称和URL不能为空！")
            return
        
        # 确保URL以http://或https://开头
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            
        if not self.is_valid_url(url):
            messagebox.showerror("错误", "URL格式无效！")
            return
        
        # 生成唯一ID
        site_id = f"{category}_{len(self.websites)+1}"
        new_site = {
            "id": site_id,
            "name": name,
            "url": url,
            "category": category,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 保存数据
        self.websites.append(new_site)
        self.save_websites()
        
        # 重新生成按钮
        self.populate_buttons()
        
        # 清空输入
        self.name_entry.delete(0, tk.END)
        self.url_entry.delete(0, tk.END)
        self.update_status(f"已添加网站: {name}")
        
    def populate_buttons(self):
        """刷新按钮显示 - 使用网格布局"""
        # 清空现有按钮
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # 按分类过滤
        filtered = self.websites
        if self.current_filter != "全部":
            filtered = [s for s in self.websites if s["category"] == self.current_filter]
        
        # 如果没有网站，显示提示
        if not filtered:
            ttk.Label(self.scroll_frame, text="没有找到网站", 
                     font=("Helvetica", 12), 
                     foreground="#999").pack(pady=20)
            self.update_status(f"显示 {len(filtered)} 个网站")
            return
        
        # 使用网格布局排列按钮
        cols = 4  # 每行显示4个按钮
        for i, site in enumerate(filtered):
            row, col = divmod(i, cols)
            
            # 创建按钮框架
            btn_frame = ttk.Frame(self.scroll_frame, padding=5)
            btn_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # 创建按钮
            btn = ttk.Button(btn_frame, text=site["name"], 
                           command=lambda u=site["url"]: webbrowser.open(u),
                           width=15)
            btn.pack(fill=tk.BOTH, expand=True)
            
            # 添加右键菜单
            btn.bind("<Button-3>", lambda e, sid=site["id"]: self.show_context_menu(e, sid))
            
            # 配置网格列权重
            if col == 0:
                self.scroll_frame.grid_rowconfigure(row, weight=0)
            self.scroll_frame.grid_columnconfigure(col, weight=1)
        
        self.update_status(f"显示 {len(filtered)} 个网站")
        
    def show_context_menu(self, event, site_id):
        """右键菜单"""
        menu = tk.Menu(self.scroll_frame, tearoff=0)
        menu.add_command(label="删除", command=lambda sid=site_id: self.delete_site(sid))
        menu.tk_popup(event.x_root, event.y_root)
        
    def delete_site(self, site_id):
        """删除网站"""
        site_name = next((s["name"] for s in self.websites if s["id"] == site_id), "")
        if not site_name:
            return
            
        if not messagebox.askyesno("确认删除", f"确定要删除网站 '{site_name}' 吗？"):
            return
            
        self.websites = [s for s in self.websites if s["id"] != site_id]
        self.save_websites()
        self.populate_buttons()
        self.update_status(f"已删除网站: {site_name}")
        
    def filter_sites(self, category):
        """分类过滤"""
        self.current_filter = category
        self.populate_buttons()
        
    def search_website(self):
        """搜索功能"""
        keyword = self.search_entry.get().strip().lower()
        if not keyword:
            self.populate_buttons()
            return
        
        filtered = [s for s in self.websites 
                   if keyword in s["name"].lower() or keyword in s["url"].lower()]
        
        # 清空现有按钮
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # 如果没有结果，显示提示
        if not filtered:
            ttk.Label(self.scroll_frame, text="没有找到匹配的网站", 
                     font=("Helvetica", 12), 
                     foreground="#999").pack(pady=20)
            self.update_status(f"找到 {len(filtered)} 个匹配结果")
            return
        
        # 使用网格布局排列搜索结果
        cols = 4  # 每行显示4个按钮
        for i, site in enumerate(filtered):
            row, col = divmod(i, cols)
            
            # 创建按钮框架
            btn_frame = ttk.Frame(self.scroll_frame, padding=5)
            btn_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # 创建按钮
            btn = ttk.Button(btn_frame, text=site["name"], 
                           command=lambda u=site["url"]: webbrowser.open(u),
                           width=15)
            btn.pack(fill=tk.BOTH, expand=True)
            
            # 添加右键菜单
            btn.bind("<Button-3>", lambda e, sid=site["id"]: self.show_context_menu(e, sid))
            
            # 配置网格列权重
            if col == 0:
                self.scroll_frame.grid_rowconfigure(row, weight=0)
            self.scroll_frame.grid_columnconfigure(col, weight=1)
        
        self.update_status(f"找到 {len(filtered)} 个匹配结果")
        
    def reset_search(self):
        """重置搜索"""
        self.search_entry.delete(0, tk.END)
        self.populate_buttons()
        
    def save_websites(self):
        """保存数据到文件"""
        try:
            # 创建备份
            if os.path.exists(self.data_file):
                backup_file = self.data_file + ".bak"
                shutil.copy2(self.data_file, backup_file)
                
            with open(self.data_file, "w", encoding="utf-8") as f:
                for site in self.websites:
                    f.write(json.dumps(site, ensure_ascii=False) + "\n")
        except Exception as e:
            messagebox.showerror("错误", f"保存数据失败: {str(e)}")
            
    def update_status(self, message):
        """更新状态栏"""
        self.status.config(text=message)

if __name__ == "__main__":
    root = tk.Tk()
    app = WebLauncherApp(root)
    root.mainloop()