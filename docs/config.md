# 配置

```toml
# MongoDB 服务器连接 URL
conn_str = "" 
# MongoDB 数据库名
database_name = "akiwa" 
# 监听弹幕命令列表，通常无需更改
commands = ["INTERACT_WORD", "ENTRY_EFFECT", "DANMU_MSG", "SEND_GIFT", "COMBO_SEND", "SUPER_CHAT_MESSAGE", "GUARD_BUY",  "LIKE_INFO_V3_UPDATE", "WATCHED_CHANGE", "ONLINE_RANK_COUNT", "POPULAR_RANK_CHANGED", "POPULARITY_RED_POCKET_NEW"]
# 日志等级
log_level = "DEBUG"
# 定时任务执行间隔（如关注数，舰长数监听等）
schedule_interval = 300 # seconds

[listening]
# 监听直播间ID，支持短ID
room = []
# 监听用户ID
user = []
# 直播状态检测间隔
check_interval = 30 # seconds

# 统计服务相关
[service]
host = "127.0.0.1"
port = "12345"

# 外置弹幕监听器相关
[yomiuri]
# 是否启用 Yomiuri
enable = false
# Yomiuri验证Token
token = ""

# 账户相关（目前仅用于未开启 Yomiumi 时的弹幕监听）
[account]
# 参考 https://nemo2011.github.io/bilibili-api/#/get-credential 以获取Bilibili账户凭证
sessdata = ""
bili_jct = ""
buvid3 = ""
deaduserid = ""
# 可选
ac_time_value = ""

# 图标渲染相关
[render]
# Seaborn图标风格，可选项：darkgrid、whitegrid、dark、white、ticks。参见 https://seaborn.pydata.org/tutorial/aesthetics.html#seaborn-figure-styles
seaborn_style = "whitegrid"
# 渲染用字体，可使用字体路径或字体名称，请确保运行环境中已安装该字体且支持中文
font = "Noto Sans SC"

# Jieba分词相关
# 如需将多行文字转换成列表，可使用 https://arraythis.com/
[jieba]
# 自定义词汇
words = []
# 忽略词汇，在进行分词前去除在此列表的弹幕
ignore_words = []
# 停用词汇，在分词后去除在此列表的词汇，默认使用哈工大停用词表
stop_words = []
```