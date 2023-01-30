import time
import json
import uuid
from khl import Message,PrivateMessage,ChannelPrivacyTypes,Bot
from khl.card import Card,CardMessage,Module,Types,Element
from typing import Union

# 读取config文件
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
bot = Bot(token=config['token'])

bmUrl = "https://api.battlemetrics.com" #bm api的父url
kookUrl="https://www.kookapp.cn"# kook api的父url
kookHeaders={f'Authorization': f"Bot {config['token']}"}

# 获取当前时间
def GetTime():
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

# 获取uuid
def get_uuid():
    get_timestamp_uuid = uuid.uuid1()  # 根据 时间戳生成 uuid , 保证全球唯一
    return get_timestamp_uuid

# 在控制台打印msg内容，用作日志
def logging(msg: Message):
    now_time = GetTime()
    if isinstance(msg,PrivateMessage):
        print(f"[{now_time}] PrivateMessage - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}")
    else:
        print(f"[{now_time}] G:{msg.ctx.guild.id} - C:{msg.ctx.channel.id} - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}")

# 获取错误信息卡片
def log_err_cm(err_str:str):
    cm2 = CardMessage()
    c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json/data错误是因为查询结果不存在"),Module.Divider())
    c.append(Module.Section(Element.Text(f"{err_str}\n您可能需要重新操作",Types.Text.KMD)))
    c.append(Module.Divider())
    c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
        Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
    cm2.append(c)
    return cm2


#更新卡片消息
async def upd_card(msg_id: str,
                   content,
                   target_id='',
                   channel_type: Union[ChannelPrivacyTypes, str] = 'public',
                   bot=bot):
    content = json.dumps(content)
    data = {'msg_id': msg_id, 'content': content}
    if target_id != '':
        data['temp_target_id'] = target_id
    if channel_type == 'public' or channel_type == ChannelPrivacyTypes.GROUP:
        result = await bot.client.gate.request('POST', 'message/update', data=data)
    else:
        result = await bot.client.gate.request('POST', 'direct-message/update', data=data)
    return result