# API

## 直播类

### 获取所有记录的直播

GET `/live/all`

返回示例：
```json
{
  "data": [
    {
      "live_id": "e65098db156a43968393da48484a36b8",
      "room_id": 25512485,
      "title": "【2D】晚上好",
      "start_time": 1705056939,
      "end_time": 17050668324
    }
  ],
  "error": null
}
```

### 获取某直播间的最近一次直播

GET `/live/latest/<room_id>`

返回示例：
```json
{
  "data": {
      "live_id": "e65098db156a43968393da48484a36b8",
      "room_id": 25512485,
      "title": "【2D】晚上好",
      "start_time": 1705056939,
      "end_time": 17050668324
    },
  "error": null
}
```

### 获取正在进行的直播

GET `/live/now`

返回示例：
```json
{
  "data": [
    {
      "live_id": "e65098db156a43968393da48484a36b8",
      "room_id": 25512485,
      "title": "【2D】晚上好",
      "start_time": 1705056939,
      "end_time": 0
    }
  ],
  "error": null
}
```

## 统计类

### 实时统计

#### 获取实时营收

GET `/live/<live_id>/realtime/revenue`

返回示例：
```json
{
  "data": {
    "amount": 1567.3
  },
  "error": null
}
```

#### 获取实时看过数

GET `/live/<live_id>/realtime/watched`

返回示例：
```json
{
  "data": {
    "timestamp": 1705147513,
    "value": 32056
  },
  "error": null
}
```

#### 获取实时高能用户数

GET `/live/<live_id>/realtime/paid`

返回示例：
```json
{
  "data": {
    "timestamp": 1705147513,
    "value": 1537
  },
  "error": null
}
```

#### 获取实时同接

GET `/live/<live_id>/realtime/online`

返回示例：
```json
{
  "data": {
    "timestamp": 1705147513,
    "value": 1682
  },
  "error": null
}
```

#### 获取实时高能榜

GET `/live/<live_id>/realtime/popular_rank`

返回示例：
```json
{
  "data": {
    "timestamp": 1705147513,
    "value": 3
  },
  "error": null
}
```

### 直播统计

所有直播统计类 API 默认返回 PNG 格式的图表图片。在添加参数 `data=True` 后可返回具体数据。

以下返回示例均为添加 `data=True` 后的结果。

#### 获取直播营收

GET `/live/<live_id>/revenue`

返回示例：
```json
{
  "data": {
    "amount": 6322.8
  },
  "error": null
}
```

#### 获取观众平均数据

GET `/live/<live_id>/audience_compare`

返回示例：
```json
{
  "data": [
    {"name": "人均互动条数", "value": 2.6, "category": "参与互动的观众"},
    {"name": "人均互动条数", "value": 1.3 , "category": "所有观众"},
    {"name": "人均弹幕条数", "value": 0.8, "category": "参与互动的观众"},
    {"name": "人均弹幕条数", "value": 0.6, "category": "所有观众"},
    {"name": "人均观看时长", "value": 2.4, "category": "所有观众"},
    {"name": "人均观看时长", "value": 3.8, "category": "参与互动的观众"}
  ],
  "error": null
}
```

#### 获取粉丝团数据

GET `/live/<live_id>/medal_compare`

返回示例：
```json
{
    "data": [
        {"category": "观众数量", "name": "非粉丝团", "value": 8227.0},
        {"category": "弹幕数量", "name": "非粉丝团", "value": 5887.0},
        {"category": "互动数量", "name": "非粉丝团", "value": 6733.0},
        {"category": "观众数量", "name": "1-5", "value": 13.0},
        {"category": "弹幕数量", "name": "1-5", "value": 28.0},
        {"category": "互动数量", "name": "1-5", "value": 28.0},
        {"category": "观众数量", "name": "6-10", "value": 53.0},
        {"category": "弹幕数量", "name": "6-10", "value": 111.0},
        {"category": "互动数量", "name": "6-10", "value": 111.0},
        {"category": "观众数量", "name": "11-20", "value": 220.0},
        {"category": "弹幕数量", "name": "11-20", "value": 1254.0},
        {"category": "互动数量", "name": "11-20", "value": 1255.0},
        {"category": "观众数量", "name": "21-40", "value": 238.0},
        {"category": "弹幕数量", "name": "21-40", "value": 4703.0},
        {"category": "互动数量", "name": "21-40", "value": 4763.0}
    ],
    "error": null
}
```

#### 获取词频统计

GET `/live/<live_id>/word_frequency`

返回示例：
```json
{
    "data": [
        {"category": "", "name": "虞莫", "value": 2696.0},
        {"category": "", "name": "\\", "value": 2239.0},
        {"category": "", "name": "好好", "value": 1025.0},
        {"category": "", "name": "好", "value": 1011.0},
        {"category": "", "name": "老板", "value": 923.0},
        {"category": "", "name": "礼物", "value": 919.0}
    ],
    "error": null
}
```

#### 获取弹幕词云

GET `/live/<live_id>/word_cloud`

返回示例：
```json
{
    "data": [
        ["虞莫", 2696],
        ["\\", 2239],
        ["好好", 1025],
        ["好", 1011],
        ["老板", 923]
    ],
    "error": null
}
```

#### 获取营收金额构成

GET `/live/<live_id>/revenue_scale`

返回示例：
```json
{
    "data": [
        {"name": "≤100", "value": 3672.2},
        {"name": "100-1000", "value": 8400.0},
        {"name": "≥1000", "value": 52580.0}
    ],
    "error": null
}
```

#### 获取营收类型构成（以金额记）

GET `/live/<live_id>/revenue_type_scale`

返回示例：
```json
{
    "data": [
        {"name": "超级留言", "value": 4440.0},
        {"name": "舰长", "value": 59980.0},
        {"name": "礼物", "value": 232.2}
    ],
    "error": null
}
```

#### 获取营收类型构成（以数量记）

GET `/live/<live_id>/revenue_type_scale_by_times`

返回示例：
```json
{
    "data": [
        {"name": "超级留言", "value": 69.0},
        {"name": "舰长", "value": 60.0},
        {"name": "礼物", "value": 335.0}
    ],
    "error": null
}
```

#### 获取粉丝团互动比例

GET `/live/<live_id>/medal_scale`

返回示例：
```json
{
    "data": [
        {"name": "其他", "value": 1633.0},
        {"name": "美人虞", "value": 6389.0},
        {"name": "酷诺米", "value": 1730.0},
        {"name": "无粉丝团", "value": 968.0},
        {"name": "GOGO队", "value": 776.0},
        {"name": "柚恩蜜", "value": 766.0},
        {"name": "小莞熊", "value": 628.0}
    ],
    "error": null
}
```

#### 获取时序营收图

GET `/live/<live_id>/earning_timing`

返回示例：
```json
{
    "data": [
        {"category": "", "name": "2", "value": 0.0},
        {"category": "", "name": "3", "value": 0.7},
        {"category": "", "name": "5", "value": 4332.0},
        {"category": "", "name": "6", "value": 0.2},
        {"category": "", "name": "7", "value": 100.0}
    ],
    "error": null
}
```

#### 获取时序弹幕图

GET `/live/<live_id>/danmu_timing`

返回示例：
```json
{
    "data": [
        {"category": "", "name": "0", "value": 13.0},
        {"category": "", "name": "1", "value": 22.0},
        {"category": "", "name": "2", "value": 59.0},
        {"category": "", "name": "3", "value": 37.0},
        {"category": "", "name": "4", "value": 66.0},
        {"category": "", "name": "5", "value": 98.0}
    ],
    "error": null
}
```

#### 获取时序舰团图

GET `/live/<live_id>/guard_timing`

返回示例：
```json
{
    "data": [
        {"category": "", "name": "0", "value": 0.0},
        {"category": "", "name": "1", "value": 0.0},
        {"category": "", "name": "2", "value": 0.0},
        {"category": "", "name": "3", "value": 0.0},
        {"category": "", "name": "4", "value": 0.0},
        {"category": "", "name": "5", "value": 4.0}
    ],
    "error": null
}
```

#### 获取时序SC图

GET `/live/<live_id>/superchat_timing`

返回示例：
```json
{
    "data": [
        {"category": "", "name": "0", "value": 0.0},
        {"category": "", "name": "1", "value": 0.0},
        {"category": "", "name": "2", "value": 0.0},
        {"category": "", "name": "3", "value": 0.0},
        {"category": "", "name": "4", "value": 0.0},
        {"category": "", "name": "5", "value": 0.0}
    ],
    "error": null
}
```

#### 获取高能用户与同接时序图

GET `/live/<live_id>/paid_and_online_timing`

返回示例：
```json
{
    "data": [
        {"category": "高能用户", "name": "0", "value": 7.666666666666667},
        {"category": "高能用户", "name": "1", "value": 29.7},
        {"category": "高能用户", "name": "2", "value": 72.47826086956522},
        {"category": "高能用户", "name": "3", "value": 118.22727272727273},
        {"category": "高能用户", "name": "4", "value": 171.125},
        {"category": "高能用户", "name": "5", "value": 243.5},
        {"category": "同接", "name": "0", "value": 28.2},
        {"category": "同接", "name": "1", "value": 84.63636363636364},
        {"category": "同接", "name": "2", "value": 236.25},
        {"category": "同接", "name": "3", "value": 348.8181818181818},
        {"category": "同接", "name": "4", "value": 417.6666666666667},
        {"category": "同接", "name": "5", "value": 465.3636363636364}
    ],
    "error": null
}
```


#### 获取高能榜时序图

GET `/live/<live_id>/popular_rank_timing`

返回示例：
```json
{
    "data": [
        {"category": "", "name": "64", "value": 68.91666666666667},
        {"category": "", "name": "65", "value": 80.6},
        {"category": "", "name": "66", "value": 63.666666666666664},
        {"category": "", "name": "85", "value": 70.5},
        {"category": "", "name": "86", "value": 59.0},
        {"category": "", "name": "87", "value": 57.5},
        {"category": "", "name": "88", "value": 58.5},
        {"category": "", "name": "90", "value": 60.5},
        {"category": "", "name": "91", "value": 59.75},
        {"category": "", "name": "92", "value": 56.666666666666664}
    ],
    "error": null
}
```

#### 获取点赞时序图

GET `/live/<live_id>/like_timing`

返回示例：
```json
{
    "data": [
        {"category": "", "name": "0", "value": 1.5},
        {"category": "", "name": "1", "value": 8.833333333333334},
        {"category": "", "name": "2", "value": 110.11111111111111},
        {"category": "", "name": "3", "value": 368.6},
        {"category": "", "name": "4", "value": 494.8888888888889},
        {"category": "", "name": "5", "value": 1004.5},
        {"category": "", "name": "6", "value": 1454.1},
        {"category": "", "name": "7", "value": 1630.1666666666667},
        {"category": "", "name": "8", "value": 1729.375},
        {"category": "", "name": "9", "value": 1956.4},
        {"category": "", "name": "10", "value": 2104.285714285714}
    ],
    "error": null
}
```

#### 获取看过时序图

GET `/live/<live_id>/watched_timing`

返回示例：
```json
{
    "data": [
        {"category": "", "name": "0", "value": 0.0},
        {"category": "", "name": "1", "value": 61.54545454545455},
        {"category": "", "name": "2", "value": 305.25},
        {"category": "", "name": "3", "value": 538.9090909090909},
        {"category": "", "name": "4", "value": 725.4166666666666},
        {"category": "", "name": "5", "value": 881.0},
        {"category": "", "name": "6", "value": 1019.0},
        {"category": "", "name": "7", "value": 1155.7},
        {"category": "", "name": "8", "value": 1299.75},
        {"category": "", "name": "9", "value": 1429.909090909091},
        {"category": "", "name": "10", "value": 1502.0}
    ],
    "error": null
}
```

#### 获取粉丝增量时序图

GET `/live/<live_id>/followers_increment_timing`

返回示例：
```json
{
    "data": [
        {"category": "", "name": "0", "value": 0.0},
        {"category": "", "name": "1", "value": 0.0},
        {"category": "", "name": "2", "value": 1.0},
        {"category": "", "name": "3", "value": 0.0},
        {"category": "", "name": "4", "value": 0.0},
        {"category": "", "name": "5", "value": 0.0},
        {"category": "", "name": "6", "value": 0.0},
        {"category": "", "name": "7", "value": 0.0},
        {"category": "", "name": "8", "value": 0.0},
        {"category": "", "name": "9", "value": 0.0},
        {"category": "", "name": "10", "value": 0.0}
    ],
    "error": null
}
```