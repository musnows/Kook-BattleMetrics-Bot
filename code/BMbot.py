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

BMurl = "https://api.battlemetrics.com" #bm api的父url
kook="https://www.kookapp.cn"# kook api的父url
Botoken = config['token']
headers={f'Authorization': f"Bot {Botoken}"}
Debug_CL="6248953582412867"

# 向botmarket通信
@bot.task.add_interval(minutes=29)
async def botmarket():
    api ="http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid':'fbb98686-91fe-46b5-be2c-cf146cccc822'}
    async with aiohttp.ClientSession() as session:
        await session.post(api, headers=headers)


######################################################################################

def GetTime():
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

#添加全局print命令写入log，来得知自己什么时候重启了bot
print(f"Start at: [%s]" % GetTime())

# 在控制台打印msg内容，用作日志
def logging(msg: Message):
    now_time = GetTime()
    print(f"[{now_time}] G:{msg.ctx.guild.id} - C:{msg.ctx.channel.id} - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}")



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
    c3 = Card(Module.Header('目前bm小助手支持的指令如下！'))
    c3.append(Module.Divider())
    #实现卡片的markdown文本
    c3.append(Module.Section(Element.Text('服务器查询指令为`/BM`or`/bm`\n参数: 服务器名，游戏名，显示前几个搜索结果\n使用示例:`/BM 萌新 hll 4`\n显示游戏`hll`服务器中名称包含`萌新`的前4个结果\n\n`/py 玩家id 服务器id` 查询玩家在该服务器游玩时长\n`/sv 服务器id` 查询指定服务器的相关信息\n`/监看 服务器id 图标url` 在本频道开启对指定服务器状态的自动更新，可通过图标url为卡片消息添加个性化logo。建议分辨率128*128，且不要在图标周围留太多空白\n`/td 服务器id` 取消服务器状态更新，若不传入服务器id则默认取消本频道的全部监看',Types.Text.KMD)))
    c3.append(Module.Divider())
    c3.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
              Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
    cm.append(c3)
    await msg.reply(cm)


# 查询服务器信息
@bot.command(name='BM',aliases=['bm'])
async def BM_Check(msg: Message, name: str ="err", game: str="err",max:int = 3):
    logging(msg)
    if name == "err":
        await msg.reply(f"函数传参错误！name:`{name}`, game:`{game}`\n")
        return # 通过缺省值检查来判断是否没有传入完整参数

    if max>5:
        await msg.reply("KOOK目前仅支持显示`<=5`个卡片！")
        max=5 #修正为5个

    global ret
    try:
        url = BMurl+f'/servers?filter[search]={name}&filter[game]={game}'
        if game == "err": #如果不指定游戏，就直接搜索关键字
            url = BMurl+f'/servers?filter[search]={name}'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                ret = json.loads(await response.text())

        count = 1
        cm1 = CardMessage()
        for server in ret['data']:
            if count > max:
                break #只显示前max个结果
            
            #print(f"{server}  --- {type(server)}")
            emoji = ":green_circle:"
            if server['attributes']['status'] != "online":
                emoji = ":red_circle:"
            
            check_map=f"{server}"#需要判断是否包含map值
            if 'map' in check_map:
                MAPstatus=server['attributes']['details']['map']
            else:
                MAPstatus="-"
            
            c = Card(Module.Header(f"{server['attributes']['name']}"), Module.Context(f"id: {server['id']},  ip端口 {server['attributes']['ip']}:{server['attributes']['port']}\n"))
            c.append(Module.Divider())
            c.append(
                Module.Section(
                    Struct.Paragraph(3,
                        Element.Text(f"**状态 **\n" +  f"{emoji}" + "   \n" + "**地图 **\n" + f"{MAPstatus}",
                                    Types.Text.KMD),
                        Element.Text(f"**服务器ip \n**" + f"{server['attributes']['ip']}" + "     \n"+"**Rank **\n" + f"#{server['attributes']['rank']}",
                                    Types.Text.KMD),
                        Element.Text(f"**当前地区 \n**" + f"{server['attributes']['country']}" + "    \n"+"**Players **\n"f"{server['attributes']['players']}/{server['attributes']['maxPlayers']}",
                                    Types.Text.KMD))))       
            c.append(Module.Context(Element.Text(f"在bm官网查看详细信息/加入游戏 [{server['id']}](https://www.battlemetrics.com/servers/{server['relationships']['game']['data']['id']}/{server['id']})",Types.Text.KMD)))

            cm1.append(c)
            count += 1

        await msg.reply(cm1)

    except Exception as result:
        #print(f"{type(result)}--{type(ret)}")
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json/data错误是因为查询结果不存在"))
        c.append(Module.Divider())
        c.append(Module.Section(f"【报错】  {result}\n\n【api返回错误】 {ret}\n"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
              Element.Button('帮助', 'https://kook.top/Lsv21o', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


# 通过关键字查找玩家
@bot.command(name='spy',aliases=['查找玩家'])
async def player_id(msg: Message, key:str='err',game:str='err'):
    logging(msg)
    if key == 'err':
        await msg.reply(f"函数传参错误！player_name:`{key}`\n")
        return # 通过缺省值检查来判断是否没有传入完整参数
    
    global ret1
    try:
        url1 = BMurl+f'/players?filter[search]={key}'
        if game != 'err':
            url1 = BMurl+f'/players?filter[search]={key}&filter[server][game]={game}'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url1) as response:
                ret1 = json.loads(await response.text())

        count = 1
        cm1 = CardMessage()
        c = Card(Module.Header(f"玩家BM-ID查询结果如下"), Module.Context(f"若出现同名，请尝试根据创号时间定位你的bm-id"))
        for p in ret1['data']:
            if count > 4:
                break #只显示前4个结果
            
            c.append(Module.Divider())
            c.append(Module.Section(
                Element.Text(f"`BM-ID` {p['attributes']['id']}\n"
                +f"`昵称` {p['attributes']['name']}\n"
                +f"`创号时间` {p['attributes']['createdAt']}\n",Types.Text.KMD)))
            
            count+=1

        c.append(Module.Divider())
        c.append(Module.Section(Element.Text("BM-api没有提供能定位**同名用户**的返回值，只能通过指定游戏+看创号时间的方式来曲线救国。如果你无法准确定位，可尝试前往bm官网进行查询 [bm/players](https://www.battlemetrics.com/players)",Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
              Element.Button('帮助', 'https://kook.top/Lsv21o', Types.Click.LINK)))
        cm1.append(c)
        await msg.reply(cm1)

    except Exception as result:
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json/data错误是因为查询结果不存在"))
        c.append(Module.Divider())
        c.append(Module.Section(f"【报错】  {result}\n\n【api返回错误】 {ret1}\n"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
              Element.Button('帮助', 'https://kook.top/Lsv21o', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)
            
    

    

# 查看玩家在某个服务器玩了多久，需要玩家id和bm服务器id
@bot.command(name='py',aliases=['player'])
async def player_check(msg: Message, player_id: str="err", server_id: str="err"):
    logging(msg)
    if player_id == "err" or server_id == "err":
        await msg.reply(f"函数传参错误！player_id:`{player_id}`, server_id:`{server_id}`\n")
        return # 通过缺省值检查来判断是否没有传入完整参数

    global ret1
    try:
        url1 = BMurl+f'/players/{player_id}/servers/{server_id}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url1) as response:
                ret1 = json.loads(await response.text())

        sec = ret1['data']['attributes']['timePlayed']
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        time_played = f"{h}时{m}分{s}秒"

        url2=BMurl+f"/servers/{server_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url2) as response:
                ret2 = json.loads(await response.text())

        server_name = ret2['data']['attributes']['name']
        await msg.reply(f"你已经在服务器: `{server_name}`\n玩了{time_played}，真不错！")

    except Exception as result:
        cm = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json/data错误是因为查询结果不存在"))
        c.append(Module.Divider())
        c.append(Module.Section(f"【报错】  {result}\n\n【api返回错误】  {ret1['errors']}\n"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
              Element.Button('帮助', 'https://kook.top/Lsv21o', Types.Click.LINK)))
        cm.append(c)
        await msg.reply(cm)


#####################################服务器实时监控############################################

# 检查指定服务器并更新
async def ServerCheck_ID(id:str,icon:str=""):
    url = f"https://api.battlemetrics.com/servers/{id}"# bm服务器id
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            ret1 = json.loads(await response.text())

        #print(f"\nGET: {ret1}\n") #取消打印，只有出现问题的时候再打印
        server = ret1['data']
        # 确认状态情况
        emoji = ":green_circle:"
        if server['attributes']['status'] != "online":
            emoji = ":red_circle:"

        #需要判断是否包含map值
        check_map=f"{server}"
        if 'map' in check_map:
            MAPstatus=server['attributes']['details']['map']
        else:
            MAPstatus="-"

        cm = CardMessage()
        if icon == "": #没有图标
            c = Card(Module.Header(f"{server['attributes']['name']}"), Module.Context(f"id: {server['id']}"))
        else: #有图标
            c = Card(
            Module.Section(
                Element.Text(f"{server['attributes']['name']}",
                                Types.Text.KMD),
                Element.Image(
                    src="https://s1.ax1x.com/2022/07/24/jXqRL8.png",
                    circle=True,
                    size='sm')))

        c.append(Module.Divider())
        c.append(
            Module.Section(
                Struct.Paragraph(
                    3,
                    Element.Text(
                        f"**状态 **\n" + f"{emoji}" + "   \n" + "**地图 **\n" +
                        f"{MAPstatus}",
                        Types.Text.KMD),
                    Element.Text(
                        f"**服务器ip \n**" + f"{server['attributes']['ip']}" +
                        "     \n" + "**rank **\n" +
                        f"#{server['attributes']['rank']}",
                        Types.Text.KMD),
                    Element.Text(
                        f"**当前地区 \n**" +
                        f"{server['attributes']['country']}" + "    \n" +
                        "**Players **\n"
                        f"{server['attributes']['players']}/{server['attributes']['maxPlayers']}",
                        Types.Text.KMD))))

        #steam://connect/{server['attributes']['ip']}:{server['attributes']['port']}
        c.append(Module.Context(Element.Text(f"在bm官网查看[详细信息](https://www.battlemetrics.com/servers/{server['relationships']['game']['data']['id']}/{server['id']}) 或 [直接加入游戏](https://www.kookapp.cn/go-wild.html?url=steam://connect/{server['attributes']['ip']}:{server['attributes']['port']})",Types.Text.KMD)))

        cm.append(c)
        return cm
       
 
# 手动指定服务器id查询
@bot.command(name='sv',aliases=['server'])
async def check_server_id(msg:Message,server:str="err"):
    logging(msg)
    if server == "err":
        await msg.reply(f"函数传参错误！server_id:`{server}`\n")
        return

    try:
        cm = await ServerCheck_ID(server)
        await msg.reply(cm)

    except Exception as result:
        cm = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json/data错误是因为查询结果不存在\n"))
        c.append(Module.Divider())
        c.append(Module.Section(f"【报错】  {result}\n\n"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/Lsv21o', Types.Click.LINK)))
        cm.append(c)
        await msg.reply(cm)


# 用于保存实时监控信息的字典
ServerDict = {
    'guild': '', 
    'channel': '', 
    'bm_server':'', 
    'icon': '', 
    'msg_id': ''
}

#保存服务器id的对应关系
@bot.command(name='BMlook',aliases=['监看'])
async def save_dict(msg: Message,server:str="err",icon:str=""):
    logging(msg)
    if server == "err":
        await msg.reply(f"函数传参错误！server_id:`{server}`\n")
        return
    try:
        global  ServerDict
        ServerDict['guild']=msg.ctx.guild.id
        ServerDict['channel']=msg.ctx.channel.id
        ServerDict['bm_server']=server
        ServerDict['icon']=icon

        flag = 0
        with open("./log/server.json",'r',encoding='utf-8') as fr1:
            data = json.load(fr1)
        for s in data:
            if s['guild'] == msg.ctx.guild.id and s['channel'] == msg.ctx.channel.id and s['bm_server'] == server:
                s['icon']= icon #如果其余三个条件都吻合，即更新icon
                flag =1
                break

        if flag ==1 and icon !="":
            await msg.reply(f"服务器图标已更新为[{s['icon']}]({s['icon']})")
        elif flag ==1 and icon =="":
            await msg.reply(f"本频道已经订阅了服务器{server}的更新信息")
        else:
            ch=await bot.fetch_public_channel(ServerDict['channel'])
            cm1 =await ServerCheck_ID(ServerDict['bm_server'],ServerDict['icon'])#获取卡片消息
            #通过函数获取卡片消息返回值，如果服务器id正确则一切正常，如果服务器id不正确则会触发except
            #避免出现先回复“服务器监看系统已添加” 又报错的情况。同时错误的内容也不会被存入文件
            
            # ↓服务器id错误时不会执行下面的↓
            await msg.reply(f'服务器监看系统已添加！')
            #服务器id正确，直接发送一条状态消息作为第一个msg
            sent = await bot.send(ch,cm1)
            ServerDict['msg_id']= sent['msg_id']#设置第一个msg_id
            #将完整的ServerDict添加进list
            data.append(ServerDict)
        
        #不管是否已存在，都需要重新执行写入（更新/添加）
        with open("./log/server.json",'w',encoding='utf-8') as fw1:
            json.dump(data,fw1,indent=2,sort_keys=True, ensure_ascii=False)        
        fw1.close()

    except Exception as result:
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json/data错误是因为查询结果不存在\n"))
        c.append(Module.Divider())
        c.append(Module.Section(f"【报错】  {result}\n\n您可能需要重新设置本频道的监看事件"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/Lsv21o', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


# 删除在某个频道的监看功能(需要传入服务器id，否则默认删除全部)
@bot.command(name='td',aliases=['退订'])#td退订
async def Cancel_Dict(msg: Message,server:str=""):
    logging(msg)
    global  ServerDict
    emptyList = list() #创建空list
    with open("./log/server.json",'r',encoding='utf-8') as fr1:
        data = json.load(fr1)
    flag=0 #用于判断
    for s in data:
        #如果吻合，则执行删除操作
        if s['guild'] == msg.ctx.guild.id and s['channel'] == msg.ctx.channel.id and s['bm_server']==server:
            flag=1
            print(f"Cancel: G:{s['guild']} - C:{s['channel']} - BM:{s['bm_server']}")
            await msg.reply(f"已成功取消{server}的监看")
        elif s['guild'] == msg.ctx.guild.id and s['channel'] == msg.ctx.channel.id and server=="":
            flag=1
            print(f"Cancel: G:{s['guild']} - C:{s['channel']} - BM: ALL")
            await msg.reply(f"已成功取消本频道下所有监看")
        else: # 不吻合，进行插入
            #先自己创建一个元素
            ServerDict['guild']=s['guild']
            ServerDict['channel']=s['channel']
            ServerDict['bm_server']=s['bm_server']
            ServerDict['icon']=s['icon']
            ServerDict['msg_id']=s['msg_id']
            #插入进空list
            emptyList.append(ServerDict)

    #最后重新执行写入
    with open("./log/server.json",'w',encoding='utf-8') as fw1:
        json.dump(emptyList,fw1,indent=2,sort_keys=True, ensure_ascii=False)        
    fw1.close()

    if flag == 0:
        await msg.reply(f"本频道暂未开启任何服务器监看")


# 实时检测并更新
@bot.task.add_interval(minutes=20)
async def update_Server():
    try:
        with open("./log/server.json",'r',encoding='utf-8') as fr1:
            bmlist = json.load(fr1)

        for s in bmlist:
            print("Updating: %s"%s)
            gu=await bot.fetch_guild(s['guild'])
            ch=await bot.fetch_public_channel(s['channel'])
            #BMid=s['bm_server']
            cm =await ServerCheck_ID(s['bm_server'],s['icon'])#获取卡片消息
            
            now_time = GetTime()
            if s['msg_id'] != "":
                url = kook+"/api/v3/message/delete"#删除旧的服务器信息
                params = {"msg_id":s['msg_id']}
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, data=params,headers=headers) as response:
                            ret=json.loads(await response.text())
                            print(f"[{now_time}] Delete:{ret['message']}")#打印删除信息的返回值

            sent = await bot.send(ch,cm)
            s['msg_id']= sent['msg_id']# 更新msg_id
            print(f"[{now_time}] SENT_MSG_ID:{sent['msg_id']}\n")#打印日志
            
        with open("./log/server.json", "w", encoding='utf-8') as f:
            json.dump(bmlist, f,indent=2,sort_keys=True, ensure_ascii=False)
        f.close()

    except Exception as result:
        err_str=f"ERR! [{GetTime()}] update_server {result}"
        print(err_str)
        #发送错误信息到指定频道
        debug_channel= await bot.fetch_public_channel(Debug_CL)
        await bot.send(debug_channel,err_str)





# 开跑！
bot.run()
