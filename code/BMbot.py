# encoding: utf-8:
import uuid
import json
import aiohttp
import time
import traceback

from typing import Union
from copy import deepcopy
from khl import Bot, Message,PrivateMessage,ChannelPrivacyTypes
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


# 在控制台打印msg内容，用作日志
def logging(msg: Message):
    now_time = GetTime()
    if isinstance(msg,PrivateMessage):
        print(f"[{now_time}] PrivateMessage - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}")
    else:
        print(f"[{now_time}] G:{msg.ctx.guild.id} - C:{msg.ctx.channel.id} - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}")


# 测试bot是否上线
@bot.command(name='hi',aliases=['HI'])
async def world(msg: Message):
    logging(msg)
    await msg.reply('world!')

# 帮助命令
@bot.command(name='BMhelp')
async def Help(msg: Message):
    logging(msg)
    cm = CardMessage()
    c3 = Card(Module.Header('目前bm小助手支持的指令如下！'),Module.Context(Element.Text("由MOAR#7134开发，开源代码见 [Github](https://github.com/Aewait/Kook-BattleMetrics-Bot)",Types.Text.KMD)))
    c3.append(Module.Divider())
    #实现卡片的markdown文本
    text ="`/hi` 查看bm小助手是否在线\n\n"
    text+="服务器查询指令为`/BM`or`/bm`\n参数: 服务器名，游戏名，显示前几个搜索结果\n"
    text+="```\n使用示例: /BM 萌新 hll 4\n显示游戏`hll`服务器中名称包含`萌新`的前4个结果\n```\n\n"
    text+="`/spy 玩家昵称` 通过昵称检索玩家（暂无法解决同名问题）\n"
    text+="`/py 玩家id 服务器id` 查询玩家在该服务器游玩时长;\n"
    text+="`/sv 服务器id` 查询指定服务器的相关信息;\n"
    text+="`/监看 服务器id 图标url` 在本频道开启对指定服务器状态的自动更新，可通过图标url为卡片消息添加个性化logo。建议分辨率`128*128`，且不要在图标周围留太多空白;\n"
    text+="`/td 服务器id` 取消服务器状态更新，若不传入服务器id则默认取消本频道的全部监看"
    c3.append(Module.Section(Element.Text(text,Types.Text.KMD)))
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
        err_str=f"ERR! [{GetTime()}] bm\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json/data错误是因为查询结果不存在"),Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n您可能需要重新操作",Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
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
        err_str=f"ERR! [{GetTime()}] spy\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json/data错误是因为查询结果不存在"),Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n您可能需要重新操作",Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
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
        err_str=f"ERR! [{GetTime()}] py\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json/data错误是因为查询结果不存在"),Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n您可能需要重新操作",Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


#####################################服务器实时监控############################################

with open("./log/server.json",'r',encoding='utf-8') as fr1:
    BmDict = json.load(fr1)

#获取uuid
def get_uuid():
    get_timestamp_uuid = uuid.uuid1()  # 根据 时间戳生成 uuid , 保证全球唯一
    return get_timestamp_uuid

# 检查指定服务器并更新
async def ServerCheck_ID(id:str,icon:str="err"):
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
        if icon == "err" or icon == "": #没有图标
            c = Card(Module.Header(f"{server['attributes']['name']}"), Module.Context(f"id: {server['id']}"))
        else: #有图标
            c = Card(
            Module.Section(
                Element.Text(f"{server['attributes']['name']}",
                                Types.Text.KMD),
                Element.Image(
                    src=icon,
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
        err_str=f"ERR! [{GetTime()}] sv:{server}\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json/data错误是因为查询结果不存在"),Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n您可能需要重新操作",Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


#保存服务器id的对应关系
@bot.command(name='BMlook',aliases=['监看','bmlk'])
async def Add_bmlk(msg: Message,server:str="err",icon:str="err",*args):
    logging(msg)
    if server == "err":
        await msg.reply(f"函数传参错误！server_id:`{server}`")
        return
    elif args != ():
        await msg.reply(f"函数存在多余参数，请检查！\nserver: `{server}`\nicon: `{icon}`\n多余参数: `{args}`")
        return
    
    try:
        ServerDict = {
            'guild': msg.ctx.guild.id, 
            'channel': msg.ctx.channel.id, 
            'bm_server':server, 
            'icon': icon, 
            'msg_id': ''
        }

        if icon !="err" and '](' in icon:
            x1 = icon.find('](')
            x2 = icon.find(')',x1+2)
            x3 = icon[x1+2:x2]
            print('[icon]',x3)#日后用于排错
            ServerDict['icon']=x3

        flag = 0
        global BmDict
        for uid,s in BmDict['data'].items():
            if s['guild'] == msg.ctx.guild.id and s['channel'] == msg.ctx.channel.id and s['bm_server'] == server:
                s['icon']= ServerDict['icon'] #如果其余三个条件都吻合，即更新icon
                flag =1
                break
        
        if flag ==1 and icon !="err":
            await msg.reply(f"服务器图标已更新为 {s['icon']}")
        elif flag ==1 and icon =="err":
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
            key_uuid = get_uuid()
            key_uuid = str(key_uuid)
            BmDict['data'][key_uuid]={}
            BmDict['data'][key_uuid]=ServerDict
        
        #不管是否已存在，都需要重新执行写入（更新/添加）
        with open("./log/server.json",'w',encoding='utf-8') as fw1:
            json.dump(BmDict,fw1,indent=2,sort_keys=True, ensure_ascii=False) 
        #打印日志来记录是否进行了修改
        print(f"[BMlook] s:{server} ic:{ServerDict['icon']} f:{flag} [1-Modify,0-Add]")
    except Exception as result:
        err_str=f"ERR! [{GetTime()}] BMlook\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json/data错误是因为查询结果不存在"),Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n您可能需要重新操作",Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


# 删除在某个频道的监看功能(需要传入服务器id，否则默认删除全部)
@bot.command(name='td',aliases=['退订'])#td退订
async def Cancel_bmlk(msg: Message,server:str="",*args):
    logging(msg)
    try:
        global BmDict
        TempDict = deepcopy(BmDict)
        flag=0 #用于判断
        for uid,s in BmDict['data'].items():
            #如果吻合，则执行删除操作
            if s['guild'] == msg.ctx.guild.id and s['channel'] == msg.ctx.channel.id and s['bm_server']==server:
                flag=1
                del TempDict['data'][uid]#删除指定频道
                print(f"[Cancel] G:{s['guild']} - C:{s['channel']} - BM:{s['bm_server']}")
                await msg.reply(f"已成功取消{server}的监看")
                break #指定了服务器id，则只删除一个
            elif s['guild'] == msg.ctx.guild.id and s['channel'] == msg.ctx.channel.id and server=="":
                flag=2
                del TempDict['data'][uid]
                print(f"[Cancel] G:{s['guild']} - C:{s['channel']} - BM:{s['bm_server']}")
            else: #不吻合则不执行操作
                continue

        if flag == 2:
            await msg.reply(f"已成功取消本频道下所有监看")
            print(f"[Cancel.Reply] G:{msg.ctx.guild.id} - C:{msg.ctx.channel.id} - BM:ALL")
        
        if flag == 0:
            await msg.reply(f"本频道暂未开启任何服务器监看")
            print(f"[Cancel] nothing to cancel")
        else:
            #有修改，重新执行写入
            BmDict=TempDict
            with open("./log/server.json",'w',encoding='utf-8') as fw1:
                json.dump(BmDict,fw1,indent=2,sort_keys=True, ensure_ascii=False)
            print(f"[Cancel] type:{flag}  save_files")
    except Exception as result:
        err_str=f"ERR! [{GetTime()}] td\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        #发送错误信息到指定频道
        debug_channel= await bot.fetch_public_channel(Debug_CL)
        await bot.send(debug_channel,err_str)

# 实时检测并更新
@bot.task.add_interval(minutes=20)
async def update_Server_bmlk():
    print(f"[BOT.TASK] update_Server begin [{GetTime()}]")
    debug_channel = await bot.fetch_public_channel(Debug_CL)
    try:
        global BmDict
        TempDict = deepcopy(BmDict)
        for uid,s in BmDict['data'].items():
            try:
                print("[BOT.TASK] Updating: %s"%s)
                gu=await bot.fetch_guild(s['guild'])
                ch=await bot.fetch_public_channel(s['channel'])
                #BMid=s['bm_server']
                cm =await ServerCheck_ID(s['bm_server'],s['icon'])#获取卡片消息
                
                if s['msg_id'] != "":
                    url = kook+"/api/v3/message/delete"#删除旧的服务器信息
                    params = {"msg_id":s['msg_id']}
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, data=params,headers=headers) as response:
                            ret=json.loads(await response.text())
                            print(f"[BOT.TASK] Delete:{ret['message']}")#打印删除信息的返回

                sent = await bot.send(ch,cm)
                TempDict['data'][uid]['msg_id'] = sent['msg_id']# 更新msg_id
                print(f"[BOT.TASK] SENT_MSG_ID:{sent['msg_id']}")#打印日志

            except Exception as result:
                err_cur = str(traceback.format_exc())
                err_str=f"ERR! [{GetTime()}] updating {s['msg_id']}\n```\n{err_cur}\n```"
                if '没有权限' in err_cur:
                    del TempDict['data'][uid]
                    err_str+=f"\nTempDict del:{s}\n"
                #发送错误信息到指定频道
                print(err_str)
                await bot.send(debug_channel,err_str)
        
        BmDict = TempDict
        with open("./log/server.json", "w", encoding='utf-8') as f:
            json.dump(BmDict, f,indent=2,sort_keys=True, ensure_ascii=False)
        print(f"[BOT.TASK] update_Server finished [{GetTime()}]")
    except Exception as result:
        err_str=f"ERR! [{GetTime()}] update_server\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        #发送错误信息到指定频道
        await bot.send(debug_channel,err_str)


#添加全局print命令写入log，来得知自己什么时候重启了bot
print(f"Start at: [%s]" % GetTime())

# 开跑！
bot.run()
