import multiprocessing,threading,datetime,json,time,re
def allow():
    global x,BASE,BASE1,IMG_URL
    al = requests.get(folder, headers={'User-Agent': 'yaohuoid34976'}).text
    if re.search(r'<title>\d+</title>', al).group()[7:-9] == '000':
        print('云函数接单开关已关闭')
        return False
    else:
        ip = requests.get(url[:-7] + re.search(r'"./static/js/main.+?"', requests.get(url).text).group()[2:-1]).text
        BASE = re.search(r'BASE:".+?"', ip).group()[6:-1]
        BASE1 = re.search(r'BASE1:".+?"', ip).group()[7:-1]
        x = re.search(r'<title>\d+</title>', al).group()[10:-8]
        IMG_URL = re.search(r'IMG_URL:".+?"', ip).group()[9:-1]
        return re.search(r'<title>\d+</title>', al).group()[7:-8]

def login():
    try:
        l = s.get(BASE+'/CheckLogin?account=' + phone + '&password=' + password)
        if l.json()['resultdata']:
            print(phone + '登陆成功')
            return l.json()['resultdata']
        else:
            print(l.json()['message'])
            exit()
    except:
        print('系统异常登陆失败')
        exit()

def tbcode(n):
    st = s.get(BASE+'/GetBrusherInfo?token=' + token)
    list = []
    if n[0]=='1':list.append(st.json()['resultdata']['AliAccount'])
    if st.json()['resultdata']['Aliww1'] and n[1]=='1':list.append(st.json()['resultdata']['Aliww1'])
    if st.json()['resultdata']['Aliww2'] and n[2]=='1':list.append(st.json()['resultdata']['Aliww2'])
    return list

def check(BASE,token,tbl,IMG_URL,s):
    t=[]
    c = s.get(BASE+'/GetTaskList?token=' + token + '&CurrentTabIndex=0&IsNoPic=0&ChangeDate=' + time.strftime('%Y/%m/%d', time.localtime()) + '&SearchAccount=&nowPage=1&Status=0')
    for tb in tbl:
        for i in c.json()['resultdata']['list']:
            if tb in i['BrusherAliAccount']:
                if 'WaitOper' in i['Status']:
                    if i['ImgPath'][0] == 'h':
                        img = i['ImgPath']
                    else:
                        img = IMG_URL + i['ImgPath']
                    requests.post('http://pushplus.hxtrip.com/send', data=json.dumps({"token": Token, "title": '(精品)开始时间 '+i['CreateDate'][-8:-3]+' 旺旺号:'+tb,"content": {'接单账号': tb,'接单手机':phone, '任务网站': 'http://www.taoffd.com','商品主图': '<img src="' + img + '" alt="商品主图" width="100%"/>', '店铺名': i['ShopName'],'付款总价': i['NeedPayMoney'], '任务开始时间': i['CreateDate'], '商品标题': i['Title'],'注意事项': '若通过关键词找不到商品可复制做单页面的商品id，然后套一下网址：https://item.taobao.com/item.htm?id=商品id，浏览器打开收藏加购，再通过关键词搜索一般都在前几个'},"template": "json"}), headers={'Content-Type': 'application/json'})
                    print(tb+'接单成功已推送')
                    t.append(tb)
                if 'OK' in i['Status']:
                    print(tb+'今日已做满一单，请将该位对应数字置0')
                    t.append(tb)
    return list(set(tbl) - set(t))

def receive(BASE1,token,tb,s):
    res = s.get(BASE1+'/GetOrder?token=' + token + '&Aliww=' + tb, timeout=20)
    print(tb+res.json()['message'])
    if '成' in res.text or '单' in res.text:
        if '馈' in res.text:
            requests.post('http://pushplus.hxtrip.com/send', data=json.dumps({"token": Token, "title": '(精品)请先处理任务消息再来接单!',"content": {'接单账号': phone, '平台网站': 'http://www.taoffd.com'},"template": "json"}), headers={'Content-Type': 'application/json'})
            print(res.json()['message'])
        else:
            return True
    time.sleep(1)
    return

def main():
    print('微信http://nxw.so/4VlkG为您提供最高效的精品云函数服务')
    global s,token
    wait_until = datetime.datetime.now() + datetime.timedelta(hours=0.24)
    s = requests.session()
    n = allow()
    if n:
        token = login()
        tbl = check(BASE,token,tbcode(n),IMG_URL,s)
        for tb in tbl:
            print(tb+'开始'+x+'线程接单请耐心等待...')
            p=multiprocessing.Process(target=thread,args=(wait_until,BASE,BASE1,IMG_URL,token,tb,s,x))
            p.start()

def thread(wait_until,BASE,BASE1,IMG_URL,token,tb,s,x):
    for i in range(int(x)):
        t=threading.Thread(target=submain,args=(wait_until,BASE,BASE1,IMG_URL,token,tb,s))
        t.start()

def submain(wait_until,BASE,BASE1,IMG_URL,token,tb,s):
    global break_loop
    while not break_loop:
        try:
            if receive(BASE1,token,tb,s):
                if not check(BASE,token,[tb],IMG_URL,s):
                    break_loop = True
        except:
            pass
        if wait_until < datetime.datetime.now():
            break_loop = True
            print(tb+'接单即将超时，该线程已停止，任务将在下次触发继续执行')
            
url = 'http://bbgg.bfxlonely.com:9660/#/main'
break_loop = False
main()
