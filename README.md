<div align="center">

# Akiwa

哔哩哔哩数据统计分析器，强大，快速，通用，可扩展。

项目名来自岬鹭宫作品[《三角的距离无限趋近零》](https://zh.wikipedia.org/zh-cn/%E4%B8%89%E8%A7%92%E7%9A%84%E8%B7%9D%E9%9B%A2%E7%84%A1%E9%99%90%E8%B6%A8%E8%BF%91%E9%9B%B6)的水濑秋玻（Minase **Akiwa**）
</div>

## 功能
<details>
<summary></summary>

- 数据监听
  - 弹幕监听
    - [x] 弹幕
    - [x] 上舰
    - [x] 礼物（含红包）
    - [x] 超级留言
    - [x] 入场
    - [x] 看过
    - [x] 点赞
    - [x] 高能用户
    - [x] 同接
    - [x] 高能榜
    - [x] 关注
  - [x] 直播状态监听
  - 用户数据监听
    - [x] 粉丝数
    - [x] 舰长数
- 实时数据
  - [x] 营收
  - [x] 高能用户数
  - [x] 同接
  - [x] 高能榜
- 直播数据
  - [x] 观众平均数据（弹幕数量/互动数量/观看时长）
  - [x] 粉丝团数据（观众数量/弹幕数量/互动数量）
  - [x] 词频统计
  - [x] 弹幕词云
  - [x] 营收金额构成
  - [x] 营收类型构成（以金额记/以数量记）
  - [x] 粉丝团互动比例
  - [x] 时序营收图
  - [x] 时序弹幕图
  - [x] 时序舰团图
  - [x] 时序SC图
  - [x] 高能用户与同接时序图
  - [x] 高能榜时序图
  - [x] 点赞时序图
  - [x] 看过时序图
  - [x] 粉丝增量时序图

</details>

## 部署

### 先决条件

- 部署MongoDB服务

```shell
# 如果未安装Poetry
pip install poetry
git clone https://github.com/WorldObservationLog/Akiwa.git
cd Akiwa
cp config.example.toml config.toml
nano config.toml # 参照Wiki中的配置条目进行配置
poetry install
poetry run python main.py
```

## 致谢

- [Code4Epoch/Bolaris](https://github.com/Code4Epoch/Bolaris)
- [Graia Project](https://github.com/GraiaProject)
- [EOE温暖大家庭](https://t.me/Eoesfamily)