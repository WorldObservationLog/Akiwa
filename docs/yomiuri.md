# Yomiuri
[Yomiuri](https://github.com/WorldObservationLog/Yomiuri) 是 Akiwa 的外置弹幕监听器，用于在严苛的风控条件下支持多直播间弹幕的监听。

默认情况下，Akiwa 使用内置的弹幕监听器（src.collectors.danmu）。受 Bilibili 风控限制，尽管在程序上 Akiwa 的内置弹幕监听器支持多直播间监听，但实际上其他直播间会出现无法接收弹幕的情况。

## 部署

### 先决条件

如需在不同机器上部署，请确保部署 Akiwa 的机器拥有公网IP或可以其他方式建立与 Yomiuri 监听端的连接。

### Akiwa 侧
在 `config.toml` 中将 `yomiuri.enable` 设为 `true`，并设置 `yomiuri.token` 以防止未经授权的 Yomiuri 监听端建立连接。

### Yomiuri 侧
获取 Bilibili Cookies 并将其拼接成形如 `bili_jct=XXX;sessdata=XXX;dedeuserid=XXX;buvid3=XXX` 的字符串。

执行命令 `yomiuri --url http://127.0.0.1:12345/?token=114514 --cookies bili_jct=XXX;sessdata=XXX;dedeuserid=XXX;buvid3=XXX`

其中的 `url` 参数需根据具体情况进行修改。