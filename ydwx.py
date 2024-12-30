#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "6,10,15 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('一点万象签到')

import requests
import time
import hashlib
import json
import os

# 一点万向签到领万向星 可抵扣停车费
# 登录后搜索https://app.mixcapp.com/mixc/gateway域名随意一个 请求体里面的deviceParams，token 多账号填多个单引号里面 用英文逗号隔开
# 本地运行用取消下面两行注释 并注释掉青龙变量的两行变量
# ydwx_deviceParams=['deviceParams1','deviceParams2']
# ydwx_token =['token1','token2']

# 青龙变量 ydwx_deviceParams ydwx_token
ydwx_deviceParams = os.getenv("ydwx_deviceParams")
ydwx_token = os.getenv("ydwx_token")

# 推送加 token
plustoken = os.getenv("plustoken")

def Push(contents):
    # plustoken推送
    if plustoken: # 检查plustoken是否为空
        headers = {'Content-Type': 'application/json'}
        json_data = {"token": plustoken, 'title': '一点万象签到', 'content': contents.replace('\n', '<br>'), "template": "json"}
        try:
            resp = requests.post('http://www.pushplus.plus/send', json=json_data, headers=headers, timeout=5).json() # 添加超时
            print('push+推送成功' if resp['code'] == 200 else f'push+推送失败: {resp.get("msg")}') # 打印错误信息
        except requests.exceptions.RequestException as e:
            print(f"push+推送请求异常: {e}")
    else:
        print("未配置plustoken，跳过推送")

if not ydwx_deviceParams or not ydwx_token:
    print("未配置ydwx_deviceParams或ydwx_token，请检查环境变量")
    exit()

ydwx_deviceParams = ydwx_deviceParams.split('&')
ydwx_token = ydwx_token.split('&')

print(f'共配置了{len(ydwx_deviceParams)}个账号')
log = []
for i in range(len(ydwx_deviceParams)):
    print(f'*****第{str(i + 1)}个账号*****')
    timestamp = str(int(round(time.time() * 1000)))
    md5 = hashlib.md5()
    sig = f'action=mixc.app.memberSign.sign&apiVersion=1.0&appId=68a91a5bac6a4f3e91bf4b42856785c6&appVersion=3.53.0&deviceParams={ydwx_deviceParams[i]}&imei=2333&mallNo=20014&osVersion=12.0.1&params=eyJtYWxsTm8iOiIyMDAxNCJ9&platform=h5&timestamp={timestamp}&token={ydwx_token[i]}&P@Gkbu0shTNHjhM!7F'
    md5.update(sig.encode('utf-8'))
    sign = md5.hexdigest()
    url = 'https://app.mixcapp.com/mixc/gateway'
    headers = {
        'Host': 'app.mixcapp.com',
        'Connection': 'keep-alive',
        'Content-Length': '564',  # Content-Length 可能会变，建议删除
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://app.mixcapp.com',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; PCAM00 Build/QKQ1.190918.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.92 Mobile Safari/537.36/MIXCAPP/3.42.2/AnalysysAgent/Hybrid',
        'Sec-Fetch-Mode': 'cors',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'com.crland.mixc',
        'Sec-Fetch-Site': 'same-origin',
        'Referer': 'https://app.mixcapp.com/m/m-20014/signIn?showWebNavigation=true&timestamp=1676906528979&appVersion=3.53.0&mallNo=20014',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    data = f'mallNo=20014&appId=68a91a5bac6a4f3e91bf4b42856785c6&platform=h5&imei=2333&appVersion=3.53.0&osVersion=12.0.1&action=mixc.app.memberSign.sign&apiVersion=1.0&timestamp={timestamp}&deviceParams={ydwx_deviceParams[i]}&token={ydwx_token[i]}&params=eyJtYWxsTm8iOiIyMDAxNCJ9&sign={sign}'
    try:
        html = requests.post(url=url, headers=headers, data=data, timeout=5) # 添加超时
        html.raise_for_status() # 检查HTTP状态码
        result = f'帐号{i + 1}签到结果:' + json.loads(html.text)['message']
    except requests.exceptions.RequestException as e:
        result = f'帐号{i + 1}签到出错: {e}' # 捕获请求异常
        print(f"请求异常: {e}")
    except json.JSONDecodeError as e:
        result = f'帐号{i + 1} JSON解析出错: {e}, 原始返回: {html.text}' #捕获json解析异常
        print(f"JSON解析出错: {e}, 原始返回: {html.text}")
    print(result)
    log.append(result)

log2 = '\n'.join(log) # 更简洁的字符串拼接方式
Push(contents=log2)
