# 部署

## 使用 Docker
```shell
git clone https://github.com/WorldObservationLog/Akiwa.git
cd Akiwa
cp config.example.toml config.toml
nano config.toml # 参照文档中的配置条目进行配置
vi Dockerfile # 中国大陆用户需取消 Dockerfile 11-15行注释以解决网络问题
vi docker-compose.yml
docker-compose up -d
```

## 手动部署

请预先部署MongoDB

```shell
git clone https://github.com/WorldObservationLog/Akiwa.git
cd Akiwa
cp config.example.toml config.toml
nano config.toml # 参照文档中的配置条目进行配置
poetry install
poetry run python main.py
```