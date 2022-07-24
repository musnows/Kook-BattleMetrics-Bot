# encoding: utf-8:
import json
import aiohttp
import time

from khl import Bot, Message
from khl.card import CardMessage, Card, Module, Element, Types, Struct


# 新建机器人，token 就是机器人的身份凭证
# 用 json 读取 config.json，装载到 config 里
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 用读取来的 config 初始化 bot
bot = Bot(token=config['token'])


# 向botmarket通信
@bot.task.add_interval(minutes=30)
async def botmarket():
    api ="http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid':'fbb98686-91fe-46b5-be2c-cf146cccc822'}
    async with aiohttp.ClientSession() as session:
        await session.post(api, headers=headers)
    

######################################################################################

# 在控制台打印msg内容，用作日志
def logging(msg: Message):
    now_time = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{now_time}] G:{msg.ctx.guild.id} - C:{msg.ctx.channel.id} - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} - Content:{msg.content}")


# 测试bot是否上线
@bot.command(name='hello')
async def world(msg: Message):
    logging(msg)
    await msg.reply('world!')

# 帮助命令
@bot.command(name='BMhelp')
async def Help(msg: Message):
    logging(msg)
    cm = CardMessage()
    c3 = Card(Module.Header('查询指令为`/BM`or`/bm`'))
    c3.append(Module.Divider())
    #实现卡片的markdown文本
    c3.append(Module.Section(Element.Text('参数: 服务器名，游戏名，显示前几个搜索结果\n使用示例：`/BM 萌新 hll 4`\n显示游戏`hll`服务器中名称包含`萌新`的前4个结果\n',Types.Text.KMD)))
    c3.append(Module.Divider())
    c3.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
              Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
    cm.append(c3)
    await msg.reply(cm)


# 查询服务器信息
@bot.command(name='BM',aliases=['bm'])
async def check(msg: Message, name: str, game: str,max:int = 3):
    logging(msg)
    try:
        url = f'https://api.battlemetrics.com/servers?filter[search]={name}&filter[game]={game}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                ret = json.loads(await response.text())
        
        count = 1
        cm = CardMessage()
        for server in ret['data']:
            if count > max:
                break #只显示前3个结果

            emoji = ":green_circle:"
            if server['attributes']['status'] != "online":
                emoji = ":red_circle:"
            c = Card(Module.Header(f"{server['attributes']['name']}"), Module.Context(f"id: {server['id']}"))
            c.append(Module.Divider())
            c.append(
                Module.Section(
                    Struct.Paragraph(3,
                        Element.Text(f"**状态 **\n" +  f"{emoji}" + "   \n" + "**地图 **\n" + f"{server['attributes']['details']['map']}",
                                    Types.Text.KMD),
                        Element.Text(f"**服务器ip \n**" + f"{server['attributes']['ip']}" + "     \n"+"**Rank **\n" + f"#{server['attributes']['rank']}",
                                    Types.Text.KMD),
                        Element.Text(f"**当前地区 \n**" + f"{server['attributes']['country']}" + "    \n"+"**Players **\n"f"{server['attributes']['players']}/{server['attributes']['maxPlayers']}",
                                    Types.Text.KMD))))
            cm.append(c)
            count += 1
        
        await msg.reply(cm)
    except Exception as result:
        #await msg.reply("很抱歉，发生了一些错误!\n提示:出现json错误是因为查询结果不存在\n\n报错: %s"%result)
        ret = str(result)
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json错误是因为查询结果不存在"))
        c.append(Module.Divider())
        c.append(Module.Section(f"报错:\n{result}\n"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
              Element.Button('帮助', 'https://kook.top/Lsv21o', Types.Click.LINK)))
        cm.append(c)
        await msg.reply(cm)
    
# 开跑！
bot.run()