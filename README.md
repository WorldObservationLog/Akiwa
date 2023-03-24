<div align="center">

# Akiwa
哔哩哔哩数据统计分析器，强大，快速，通用，可扩展。

项目名来自岬鹭宫作品[《三角的距离无限趋近零》](https://zh.wikipedia.org/zh-cn/%E4%B8%89%E8%A7%92%E7%9A%84%E8%B7%9D%E9%9B%A2%E7%84%A1%E9%99%90%E8%B6%A8%E8%BF%91%E9%9B%B6)的水濑秋玻（Minase **Akiwa**）
</div>

## 特性

- 多直播间数据抓取支持
- 自动生成直播数据报告并发布
- 多报告发布平台支持
- 快速部署，开箱即用

## 部署

### 先决条件

- 安装 Chromium & [ChromeDriver](https://chromedriver.chromium.org/)
- 部署MongoDB服务

```shell
# 如果未安装Poetry
pip install poetry
git clone https://github.com/WorldObservationLog/Akiwa.git
cd Akiwa
cp config.example.toml config.toml
nano config.toml # 参照Wiki中的配置条目进行配置
poetry update
poetry run python main.py
```

## 致谢
- [Code4Epoch/Bolaris](https://github.com/Code4Epoch/Bolaris)
- [Graia Project](https://github.com/GraiaProject)
- [EOE温暖大家庭](https://t.me/Eoesfamily)