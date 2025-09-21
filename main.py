# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup
from kivy.factory import Factory

import json
import os
import re
import shutil
import uuid
from datetime import datetime
import webbrowser

# 注册中文字体
LabelBase.register(
    name='MicrosoftYaHei',
    fn_regular='assets/fonts/msyh.ttf'
)

class WebsiteManager:
    """核心逻辑：网站数据管理"""
    def __init__(self):
        # 跨平台数据文件路径
        app_data_path = os.path.join(os.path.expanduser("~"), ".weblauncher")
        self.data_file = os.path.join(app_data_path, "custom_sites.json")
        os.makedirs(app_data_path, exist_ok=True)
        
        # 迁移旧数据
        self.migrate_old_data()
        
        # 加载网站数据
        self.websites = self.load_websites()
        self.current_filter = "全部"
    
    def migrate_old_data(self):
        """迁移旧版本数据"""
        old_paths = [
            os.path.join(os.path.expanduser("~"), "Library", "Application Support", "WebLauncher", "custom_sites.json"),
            os.path.join(os.getenv('APPDATA', ''), "WebLauncher", "custom_sites.json"),
            os.path.join(os.path.expanduser("~"), ".config", "WebLauncher", "custom_sites.json")
        ]
        
        for old_path in old_paths:
            if os.path.exists(old_path) and not os.path.exists(self.data_file):
                try:
                    shutil.copy2(old_path, self.data_file)
                    print(f"迁移旧数据: {old_path} -> {self.data_file}")
                except Exception as e:
                    print(f"数据迁移失败: {str(e)}")
    
    def load_websites(self):
        """加载已保存的网站数据"""
        default_sites = [
            {"id": "social_1", "name": "微博", "url": "https://weibo.com", "category": "社交"},
            {"id": "social_2", "name": "微信", "url": "https://wx.qq.com", "category": "社交"},
            {"id": "social_3", "name": "QQ", "url": "https://im.qq.com", "category": "社交"},
            {"id": "social_4", "name": "知乎", "url": "https://www.zhihu.com", "category": "社交"},
            {"id": "social_5", "name": "豆瓣", "url": "https://www.douban.com", "category": "社交"},
            {"id": "tech_1", "name": "GitHub", "url": "https://github.com", "category": "技术"},
            {"id": "tech_2", "name": "百度网盘", "url": "https://pan.baidu.com", "category": "工具"},
            {"id": "tech_3", "name": "阿里云", "url": "https://www.aliyun.com", "category": "工具"},
            {"id": "tech_4", "name": "CSDN", "url": "https://www.csdn.net", "category": "技术"},
            {"id": "tech_5", "name": "Stack Overflow", "url": "https://stackoverflow.com", "category": "技术"},
            {"id": "shopping_1", "name": "淘宝", "url": "https://www.taobao.com", "category": "购物"},
            {"id": "shopping_2", "name": "京东", "url": "https://www.jd.com", "category": "购物"},
            {"id": "shopping_3", "name": "拼多多", "url": "https://www.pinduoduo.com", "category": "购物"},
            {"id": "shopping_4", "name": "唯品会", "url": "https://www.vip.com", "category": "购物"},
            {"id": "shopping_5", "name": "网易严选", "url": "https://you.163.com", "category": "购物"},
            {"id": "news_1", "name": "腾讯新闻", "url": "https://news.qq.com", "category": "新闻"},
            {"id": "news_2", "name": "人民日报", "url": "https://www.people.com.cn", "category": "新闻"},
            {"id": "news_3", "name": "36氪", "url": "https://www.36kr.com", "category": "新闻"},
            {"id": "news_4", "name": "虎嗅", "url": "https://www.huxiu.com", "category": "新闻"},
            {"id": "video_1", "name": "哔哩哔哩", "url": "https://www.bilibili.com", "category": "视频"},
            {"id": "video_2", "name": "腾讯视频", "url": "https://v.qq.com", "category": "视频"},
            {"id": "video_3", "name": "爱奇艺", "url": "https://www.iqiyi.com", "category": "视频"},
            {"id": "video_4", "name": "优酷", "url": "https://www.youku.com", "category": "视频"},
            {"id": "video_5", "name": "芒果TV", "url": "https://www.mgtv.com", "category": "视频"},
            {"id": "education_1", "name": "知乎日报", "url": "https://daily.zhihu.com", "category": "新闻"},
            {"id": "education_2", "name": "中国大学MOOC", "url": "https://www.icourse163.org", "category": "教育"},
            {"id": "education_3", "name": "W3School", "url": "https://www.w3school.com.cn", "category": "技术"},
            {"id": "education_4", "name": "LeetCode", "url": "https://leetcode.cn", "category": "技术"},
            {"id": "live_1", "name": "斗鱼直播", "url": "https://www.douyu.com", "category": "直播"},
            {"id": "live_2", "name": "虎牙直播", "url": "https://www.huya.com", "category": "直播"},
            {"id": "ai_1", "name": "deepseek", "url": "https://www.deepseek.com/zh", "category": "工具"}
        ]
        
        if not os.path.exists(self.data_file):
            try:
                with open(self.data_file, "w", encoding="utf-8") as f:
                    for site in default_sites:
                        f.write(json.dumps(site, ensure_ascii=False) + "\n")
                return default_sites
            except Exception as e:
                print(f"创建默认数据文件失败: {str(e)}")
                return default_sites[:5]  # 返回部分默认数据
        
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
            print(f"加载数据文件失败: {str(e)}")
            return default_sites
        
        return sites or default_sites
    
    def validate_site(self, site):
        """验证网站数据有效性"""
        return ("name" in site and "url" in site and 
                isinstance(site["name"], str) and 
                isinstance(site["url"], str) and
                self.is_valid_url(site["url"]))
    
    def is_valid_url(self, url):
        """增强型URL验证"""
        regex = re.compile(
            r'^(https?://)?'  # 协议可选
            r'([A-Za-z0-9-]+\.)+[A-Za-z]{2,}'  # 域名部分
            r'(:\d+)?'  # 端口
            r'(/[/\w\.-]*)*$', re.IGNORECASE)
        return re.match(regex, url) is not None
    
    def add_website(self, name, url, category="我的"):
        """添加新网站"""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            
        if not self.is_valid_url(url):
            raise ValueError("URL格式无效")
        
        # 生成唯一ID - 使用UUID确保唯一性
        site_id = f"{category}_{uuid.uuid4().hex}"
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
        return new_site
    
    def delete_website(self, site_id):
        """删除网站"""
        original_count = len(self.websites)
        self.websites = [s for s in self.websites if s["id"] != site_id]
        if len(self.websites) < original_count:
            self.save_websites()
            return True
        return False
    
    def filter_sites(self, category):
        """分类过滤"""
        self.current_filter = category
        if category == "全部":
            return self.websites
        return [s for s in self.websites if s["category"] == category]
    
    def search_website(self, keyword):
        """搜索网站"""
        if not keyword:
            return self.filter_sites(self.current_filter)
        
        keyword = keyword.lower()
        return [s for s in self.websites 
               if keyword in s["name"].lower() or keyword in s["url"].lower()]
    
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
            return True
        except Exception as e:
            print(f"保存数据失败: {str(e)}")
            return False
    
    def get_all_categories(self):
        """获取所有分类"""
        categories = set()
        for site in self.websites:
            categories.add(site["category"])
        return sorted(categories)

class MainLayout(BoxLayout):
    """主布局类"""
    pass

class MyApp(App):
    """主应用类"""
    
    def build(self):
        # 设置窗口大小和标题
        Window.size = (1000, 700)
        Window.title = "智能官网直达工具"
        
        # 初始化核心逻辑
        self.manager = WebsiteManager()
        return MainLayout()
    
    def on_start(self):
        """应用启动时调用"""
        # 延迟加载数据，确保界面已初始化
        Clock.schedule_once(lambda dt: self.initialize_ui(), 0.1)
    
    def initialize_ui(self):
        """初始化UI"""
        try:
            # 初始化分类按钮
            self.initialize_categories()
            
            # 填充网站列表
            self.populate_website_list()
            
            # 初始化分类下拉框
            self.initialize_category_spinner()
        except Exception as e:
            self.show_error_popup(f"初始化界面失败: {str(e)}")
    
    def initialize_categories(self):
        """初始化分类按钮"""
        categories = ["我的", "全部", "社交", "购物", "视频", "音乐", "技术", "新闻", "工具", "教育", "直播", "其他"]
        
        # 清空现有按钮
        container = self.root.ids.category_container
        container.clear_widgets()
        
        for category in categories:
            # 创建分类按钮 - 使用KV文件中定义的样式
            btn = Factory.CategoryButton(
                text=category,
                size_hint=(None, None),
                size=(85, 32)
            )
            
            # 绑定点击事件
            btn.bind(on_press=lambda instance, cat=category: self.filter_sites(cat))
            
            # 添加到分类容器
            container.add_widget(btn)
    
    def initialize_category_spinner(self):
        """初始化分类下拉框"""
        categories = ["我的", "全部", "社交", "购物", "视频", "音乐", "技术", "新闻", "工具", "教育", "直播", "其他"]
        spinner = self.root.ids.category_spinner
        spinner.values = categories
    
    def populate_website_list(self):
        """填充网站列表"""
        if not hasattr(self, 'manager'):
            return
            
        # 清空现有内容
        grid = self.root.ids.website_grid
        grid.clear_widgets()
        
        # 获取当前筛选的网站
        sites = self.manager.filter_sites(self.manager.current_filter)
        
        if not sites:
            # 添加提示标签
            label = Factory.Label(
                text="没有找到网站\n点击右下角按钮添加",
                size_hint_y=None,
                height=100,
                color=(0.5, 0.5, 0.5, 1),
                font_size=14,
                font_name='MicrosoftYaHei'
            )
            grid.add_widget(label)
            self.update_status(f"显示 0 个网站")
            return
        
        # 添加网站按钮
        for site in sites:
            # 创建网站按钮 - 使用KV文件中定义的样式
            btn = Factory.WebsiteButton(
                text=site['name'],
                size_hint=(None, None),
                size=(180, 45)
            )
            btn.bind(on_press=lambda instance, url=site['url']: self.open_website(url))
            
            grid.add_widget(btn)
        
        self.update_status(f"显示 {len(sites)} 个网站")
        self.root.ids.count_label.text = f"共 {len(sites)} 个网站"
    
    def open_website(self, url):
        """打开网站"""
        try:
            webbrowser.open(url)
            self.update_status(f"正在打开: {url}")
        except Exception as e:
            self.show_error_popup(f"无法打开网址: {str(e)}")
    
    def delete_website(self, site_id):
        """删除网站"""
        try:
            if self.manager.delete_website(site_id):
                self.populate_website_list()
                self.update_status("网站已删除")
            else:
                self.show_error_popup("删除网站失败")
        except Exception as e:
            self.show_error_popup(f"删除网站时出错: {str(e)}")
    
    def filter_sites(self, category):
        """筛选网站分类"""
        try:
            self.manager.current_filter = category
            self.populate_website_list()
            self.update_status(f"显示分类: {category}")
        except Exception as e:
            self.show_error_popup(f"筛选网站时出错: {str(e)}")
    
    def search_website(self):
        """搜索网站"""
        try:
            keyword = self.root.ids.search_input.text.strip()
            sites = self.manager.search_website(keyword)
            
            grid = self.root.ids.website_grid
            grid.clear_widgets()
            
            if not sites:
                label = Factory.Label(
                    text="没有找到匹配的网站",
                    size_hint_y=None,
                    height=100,
                    color=(0.5, 0.5, 0.5, 1),
                    font_size=14,
                    font_name='MicrosoftYaHei'
                )
                grid.add_widget(label)
                self.update_status(f"搜索 '{keyword}' 没有结果")
                return
            
            # 添加搜索结果
            for site in sites:
                btn = Factory.WebsiteButton(
                    text=site['name'],
                    size_hint=(None, None),
                    size=(180, 45),
                    background_color=(0.9, 0.95, 0.9, 1)  # 浅绿色背景突出显示
                )
                btn.bind(on_press=lambda instance, url=site['url']: self.open_website(url))
                
                grid.add_widget(btn)
            
            self.update_status(f"找到 {len(sites)} 个匹配结果")
        except Exception as e:
            self.show_error_popup(f"搜索网站时出错: {str(e)}")
    
    def reset_search(self):
        """重置搜索"""
        try:
            self.root.ids.search_input.text = ""
            self.populate_website_list()
            self.update_status("已重置搜索")
        except Exception as e:
            self.show_error_popup(f"重置搜索时出错: {str(e)}")
    
    def add_website(self):
        """添加新网站"""
        try:
            name = self.root.ids.name_input.text.strip()
            url = self.root.ids.url_input.text.strip()
            category = self.root.ids.category_spinner.text
            
            if not name or not url:
                self.show_error_popup("名称和URL不能为空！")
                return
            
            new_site = self.manager.add_website(name, url, category)
            self.populate_website_list()
            self.root.ids.name_input.text = ""
            self.root.ids.url_input.text = ""
            self.update_status(f"已添加网站: {name}")
        except ValueError as e:
            self.show_error_popup(str(e))
        except Exception as e:
            self.show_error_popup(f"添加网站失败: {str(e)}")
    
    def update_status(self, message):
        """更新状态栏"""
        if hasattr(self, 'root') and hasattr(self.root, 'ids'):
            self.root.ids.status_label.text = message
    
    def show_error_popup(self, message):
        """显示错误弹窗"""
        popup = Popup(
            title='错误',
            content=Label(
                text=message,
                font_name='MicrosoftYaHei',
                padding=(20, 20)
            ),
            size_hint=(0.6, 0.4)
        )
        popup.open()

if __name__ == '__main__':
    MyApp().run()