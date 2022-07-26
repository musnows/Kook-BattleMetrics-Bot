# Kook-BattleMetrics-Bot
A Kook-Bot to search BattleMetrics-Server

BattleMetrics是一个游戏服务器聚合网站，可以追踪并查询游戏服务器当前的信息

>BM官网：https://www.battlemetrics.com/

## 如何使用？

以下是BM-bot目前支持的命令操作

| 命令                            | 简介                                                         |
| ------------------------------- | ------------------------------------------------------------ |
| `/BMhelp`                       | 帮助命令，起这个名字是防止冲突                               |
| `/BM 萌新 hll 4`                | 显示游戏`hll`服务器中名称包含`萌新`的前4个结果               |
| `/py bm玩家id bm服务器id`       | 查询玩家在该服务器的游玩时间                                 |
| `/sv bm服务器id`                | 查询指定服务器的状态                                         |
| `/BMlook bm服务器id 个性化icon` | 自动在本频道更新指定服务器的信息，可传入icon-url让卡片带上你们服务器的专属头像 |
| `/td bm服务器id`                | 取消本频道对指定服务器的监看，如果不传入服务器id，则默认取消全部监看 |


结果示例图：

<img src="https://s1.ax1x.com/2022/07/24/jjwsNd.png" wight="400px" height="330px">

<img src="https://s1.ax1x.com/2022/07/26/jzXzpF.png" wight="400px" height="175px">

## 私有部署
* 依赖项

KOOK-Bot架构基于[khl.py](https://github.com/TWT233/khl.py/tree/main)，而访问BattleMetrics的api基于`aiohttp`

因为`khl.py`包含了`aiohttp`，所以只需要执行下面命令，安装`khl.py`包即可

~~~
pip install khl.py
~~~

注：安装之前请确保你的Python版本高于`3.7`

* bot-token

在 `code/config`路径中添加`config.json`，并在里面填入以下内容来初始化你的Bot（连接方式为`websocket`）

```
{
    "token": " YOUR BOT TOKEN HERE ",
    "verify_token": "",
    "encrypt_key": ""
}
```

另外，请删除掉`L18-24`和`botmarket`相关的内容。避免接口冲突！

* 运行bot

~~~
python3 BM_main.py
~~~

## 最后

如果你觉得本项目还不错，还请点个STAR✨

有任何问题，请添加`issue`，也欢迎加入我的交流服务器向我提出 [kook邀请链接](https://kook.top/gpbTwZ)
