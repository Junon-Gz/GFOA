# coding=UTF8
import tkinter,time,math,threading
from tkinter import *
import requests,json
import sqlite3,math
from selenium import webdriver
#设置日志输出
import sys,os

code_path = os.getcwd()
# path = os.path
# disk = str(path).strip("<module 'ntpath' from ")[:2]
log_path = rf'{code_path}\GFOA\log'
chrome_path = rf'{code_path}\GoogleChrome\Chrome\chrome.exe'
driver_path = rf'{code_path}\GoogleChrome\Chrome\chromedriver.exe'
print(log_path)
print(chrome_path)
print(driver_path)

#创建日志目录
if not os.path.exists(log_path):
    print(f"创建目录{log_path}")
    os.makedirs(log_path)
sys.stdout = open(r'%s\text_%s.log'%(log_path,time.strftime("%Y%m%d%H%M%S", time.localtime())),mode='w',encoding='utf-8')

'''
TODO 当前方案被接口每秒限制4次查询
改进计划：
-x (1)用faker伪装headers中的User-Agent
-x (2)用多个cookie(结合多个User-Agent？)多进程\线程(如可行再 TODO 改进数据库表适配) 
'''


yyb_dict = {"广州天河路营业部":"301","广州黄埔大道营业部":"302","广州环市东路营业部":"303","广州花城大道营业部":"304","广州科韵路营业部":"305","广州中山三路中华广场营业部":"306","广州从化河滨南路营业部":"309","广州增城荔星大道营业部":"310","广州康王中路营业部":"311","广州黄埔东路营业部":"312","广州花都紫薇路营业部":"313","广州锦御一街营业部":"316","广州广州大道南营业部":"317","广州临江大道营业部":"318","广州农林下路营业部":"320","广州昌岗中路营业部":"367","广州江湾营业部":"369","广州洛溪新城营业部":"371","广州番禺环城东路营业部":"372","广州万博二路营业部":"373","广州宸悦路营业部":"378","全部":"1"}
com_dic = {"广州花城大道美林基业大厦营业部":"308","广州寺右新马路营业部":"315","广州分公司":"7001","北京分公司":"7002","上海分公司":"7003","深圳分公司":"7004","东莞分公司":"7005","粤东分公司":"7006","佛山分公司":"7007","粤西分公司":"7010","江苏分公司":"7013","山东分公司":"7014","浙江分公司":"7015","河北分公司":"7016","湖北分公司":"7018","成都分公司":"7020","西安分公司":"7021","福建分公司":"7023","珠海分公司":"7025","海南分公司":"7027","长春分公司":"7028","辽宁分公司":"7029","全部":"1"}
step_dic = {"一审":"1","二审":"2","电话回访":"3","回访录音审核":"4","全部":"11"}
root=tkinter.Tk()
root.title('GFOA')
root.resizable(0,0)
global cuncu, vartext,snatch_flag,headers,check_flag
vartext = tkinter.StringVar()
cuncu = {'yyb_dict': [], 'com_dic': [], 'step_dic': []}
snatch_flag = False
check_flag = False

headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': '',
        'Referer': 'http://online.gf.com.cn:8070/order',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }

def op_db(sql):
    '''
    sql:sql字符串
    '''
    try:
        conn = sqlite3.connect('mydatabase.db')
        cur = conn.cursor()
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}({time.time()})执行sql:{sql}')
        cur.execute(sql)
        if 'select' in sql.lower():
            res = [x for x in cur.fetchall()]
        else:
            res = True
    except Exception as e:
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}({time.time()}){sql}执行异常：{e}')
        if 'select' in sql.lower():
            res = []
        else:
            res = False
    finally:
        cur.close()
        conn.commit()
        conn.close()
        if 'select' not in sql.lower():
            print(f"执行结果:{res}")
        return res

def create_table():
    create_sql = 'CREATE TABLE IF NOT EXISTS "cookies" (  "cookies" TEXT,  "create_time" TEXT,  "invalid_time" TEXT);'
    op_db(create_sql)

def clear_cookie():
    clear_sql = 'DROP TABLE IF EXISTS "cookies"'
    op_db(clear_sql)

def get_cookie():
    '''
    获取cookies并存入内置数据库
    '''
    try:
        create_table()
        option = webdriver.ChromeOptions()
        option.add_argument('disable-infobars')
        option.add_experimental_option('useAutomationExtension', False)
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        prefs = {"profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1}
        option.add_experimental_option('prefs', prefs)
        option.add_argument('disable-infobars')
        option.add_argument('--start-maximized')
        option.add_argument('--lang=zh-cn')
        option.add_argument('--ignore-certificate-errors')
        option.binary_location = chrome_path
        browser = webdriver.Chrome(chrome_options=option,executable_path=driver_path)
        browser.get("http://online.gf.com.cn:8070/login")
        print(browser.title)
        while True:
            try:
                login = browser.find_element_by_xpath("//span[text()='抢']")
                if login:
                    print("登录成功")
                    break
            except Exception as e:
                pass
            time.sleep(2)
        cookie = browser.get_cookies()
        print(f"获取到cookie:{cookie}")
        cookies={}
        for val in cookie:
            cookies[val['name']] = val['value']
        print(f"拼凑cookies:{cookies}")
        insert_sql = f"INSERT INTO cookies Values ('{json.dumps(cookies)}','{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}','')"
        print(op_db(insert_sql))
    except Exception as e:
        print(f"登录模块错误:{e}")
        cookies = {}
    finally:
        browser.close()
        return cookies

def get_headers():
    #通过数据库获取cookie,如果数据库没有则登录系统获取
    try:
        global headers
        select_sql = 'select cookies from cookies where invalid_time = ""'
        cookies = op_db(select_sql)
        if len(cookies)>0:
            print(f"从数据库查询到cookie：{cookies}")
            #cookies:[(),()]
            cookie = json.loads(cookies[0][0])
        else:
            cookie = get_cookie()
            print(f"从网页获取到cookie：{cookie}")
        headers['Cookie'] = f"sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%223073538%22%2C%22\
                            first_id%22%3A%2217f45ec7f5ec68-0815ae60ce6d35-4e607a6f-2304000-17f45ec7f5f409%22%2C%22%24\
                            device_id%22%3A%2217f799926ed2d-0958a2610ff164-56171d5e-2304000-17f799926ee1065%22%7D;\
                            JSESSIONID={cookie['JSESSIONID']}; SECKEY_ABVK={cookie['SECKEY_ABVK']}; BMAP_SECKEY={cookie['BMAP_SECKEY']};\
                            token={cookie['token']}"
        print(f"拼凑得到新header：{headers}")
    except Exception as e:
        print(f"合成header错误:{e}")

def test(branch,company,step):
    # print(f"函数接收{branch,company,step}")
    url = f"http://online.gf.com.cn:8070/api/order/list?branchs={'%7C'.join(branch)}&company={'%7C'.join(company)}&enableNotification=0&orderType=1&step={'%7C'.join(step)}"
    print(f"请求{url}")

def slow_check(sleep,check_url):
    global check_flag
    while check_flag:
        try:
            time.sleep(sleep)
            response = requests.request("GET", check_url, headers=headers, data={})
            if '筛选订单成功' in response.text:
                print(f'({time.time()}){response.text}')
                response = requests.request("POST", url="http://online.gf.com.cn:8070/api/order/snatch", headers=headers, data="{}")
                print(f'({time.time()}){response.text}')
            elif time.time()%180< 1:#每180秒打印一批日志
                print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}({time.time()}){response.text}')
        except Exception as e:
            # print(f"{start_time}筛选请求异常:{str(e)}")
            if "请求异常" in str(e):
                vartext.set("登录失效，请重启软件进行登录")
                check_flag = False

def check(check_url,intv):
    global check_flag
    while check_flag:
        try:
            # start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            #筛选所有分公司营业部订单
            time.sleep(intv)
            check = requests.request("GET", check_url, headers=headers, data={})#data = playload
            #响应示例
            #{"code":0,"data":[{"orderType":1,"orderId":"632ae40c656ece6e8e308cdc","customerId":null,"branchName":"广州花都紫薇路营业部","step":4.0,"remainTime":119321,"customerName":"黄清宁","expiredTime":"2022-09-23 08:30:00","branchNo":"313"}],"msg":"筛选订单成功！"}
            if '筛选订单成功' in check.text:
                # check_time = time.time()
                # time.sleep(sleep)
                # snatch = requests.request("POST", url="http://online.gf.com.cn:8070/api/order/snatch", headers=headers, data="{}")
                print(f'({time.time()}){check.text}')
                # snatch_time = time.time()
                # print(f'({check_time}){check.text}')
                # print(f'({snatch_time}){snatch.text}')
            # elif time.time()%180 < 1:#每180秒打印一批日志
            #     # print(check_url)
            #     print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}({time.time()}){check.text}')
            # elif time.time()%190 >0.9 and time.time()%190 < 1:
            #     snatch_flag = True
            #     print(f"开抢单{snatch_flag}")
            # if response.status_code == 200:
            #     cont = json.loads(response.text)
            #     if cont['msg'] == '筛选订单成功！':
                    # TODO 如果验证查询接口没有限制，调整为查到单马上调snatch()
                    # print(f'{start_time}({time.time()}){cont["msg"]},共{len(cont["data"])}单,{cont["data"]}')
                    # snatch()
                    # order_num = len(cont["data"])
                    # if order_num > 0:
                    #     order = []#初始化订单列表
                    #     for i in range(order_num):#根据筛选订单数进行循环
                    #         have_order = snatch_order()#抢单
                    #         if have_order:#抢到单
                    #             order.append(have_order)#将订单内容添加到订单列表
                    #     print(f'{start_time}抢到{len(order)}单：{order}')
                # else:
                #     if int(start_time[17:19]) % 40 == 0:#每20秒打印一次(以便抽查频率)
                #         print(f'{start_time}({time.time()}){cont["msg"]}')
            # else:
            #     print(f'{start_time}请求异常：{response.status_code}')
            #     clear_cookie()
            #     raise Exception(f'{start_time}请求异常：{response.status_code}')
        except Exception as e:
            # print(f"{start_time}筛选请求异常:{str(e)}")
            if "请求异常" in str(e):
                vartext.set("登录失效，请重启软件进行登录")
                check_flag = False

def quick_snatch():
    global snatch_flag,headers
    while snatch_flag:
        response = requests.request("POST", url="http://online.gf.com.cn:8070/api/order/snatch", headers=headers, data="{}")
        # if time.time()%180 < 1:#每180秒打印一批日志
        #     print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}({time.time()}){response.text}')
        if "操作太过频繁" not in response.text:
            print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}({time.time()}){response.text}')

def slow_snatch(intv):
    global snatch_flag,headers
    while snatch_flag:
        time.sleep(intv)
        response = requests.request("POST", url="http://online.gf.com.cn:8070/api/order/snatch", headers=headers, data="{}")
        # if time.time()%180 < 1:#每180秒打印一批日志
        #     print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}({time.time()}){response.text}')
        if "操作太过频繁" not in response.text:
            print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}({time.time()}){response.text}')

def snatch():
    global snatch_flag
    global check_flag
    while snatch_flag:
        try:
            # print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}({time.time()})抢单')
            #抢单
            # start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # url = "http://online.gf.com.cn:8070/api/order/snatch"
            #响应示例
            #{"code":0,"data":{"orderType":1,"orderId":"632ae40c656ece6e8e308cdc","customerId":null,"branchName":"广州花都紫薇路营业部","step":4.0,"remainTime":1799,"customerName":"黄清宁","expiredTime":"2022-09-23 08:30:00","branchNo":"313"},"msg":"抢单成功！"}
            response = requests.request("POST", url="http://online.gf.com.cn:8070/api/order/snatch", headers=headers, data="{}")
            print(f'({time.time()}){response.text}')
            if '操作太过频繁' in response.text:
                continue
            snatch_flag = False
            break
            # if response.status_code == 200:
            #     cont = json.loads(response.text)
            #     if cont['msg'] == '抢单成功！':
            #         print(f'{start_time}({time.time()}){cont["msg"]}{cont["data"]}')
            #         data = cont["data"]
            #     else:
            #         # if int(start_time[17:19]) % 20 == 0:#每20秒打印一次(以便抽查频率)，同时控制日志大小
            #         #     if cont["msg"] == '操作太过频繁':
            #         #         print(f'{start_time}({time.time()})')
            #         #     else:
            #         print(f'{start_time}({time.time()}){cont["msg"]}')
            # else:
            #     print(f'({time.time()})请求异常：{response.status_code}')
            #     clear_cookie()
            #     raise Exception(f'({time.time()})请求异常：{response.status_code}')
        except Exception as e:
            print(f"({time.time()})抢单请求异常:{str(e)}")
            if "请求异常" in str(e):
                vartext.set("登录失效，请重启软件进行登录")
                snatch_flag = False
                check_flag = False

class selection:
    global cuncu, vartext
    def __init__(self,anjian,box_Vars):
        self.anjian = anjian
        self.box_Vars = box_Vars
    def start(self):
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}开启筛选')
        global cuncu, vartext,snatch_flag,check_flag
        snatch_flag = True
        check_flag = True
        if len(cuncu) == 0:
            pass
        else:
            print(f"选择了{cuncu}")
            choose_yyb = [key for x in cuncu['yyb_dict'] for key,value in yyb_dict.items() if x == int(value)]
            choose_com = [key for x in cuncu['com_dic'] for key,value in com_dic.items() if x == int(value)]
            choose_step = [key for x in cuncu['step_dic'] for key,value in step_dic.items() if x == int(value)]
            print(f"选择营业部：{','.join(choose_yyb)}\n选择分公司：{','.join(choose_com)}\n选择审核类型：{','.join(choose_step)}")
            vartext.set(str(f"选择营业部：{','.join(choose_yyb)}\n选择分公司：{','.join(choose_com)}\n选择审核类型：{','.join(choose_step)}"))
            # cuncu.clear()
        #判断全选
        if 1 in cuncu['yyb_dict']:
            cuncu['yyb_dict'] = [value for value in yyb_dict.values() if value != '1']
        else:
            cuncu['yyb_dict'] = [str(yyb) for yyb in cuncu['yyb_dict']]
        
        if 1 in cuncu['com_dic']:
            cuncu['com_dic'] = [value for value in com_dic.values() if value != '1']
        else:
            cuncu['com_dic'] = [str(yyb) for yyb in cuncu['com_dic']]
        
        if 11 in cuncu['step_dic']:
            cuncu['step_dic'] = [value for value in step_dic.values() if value != '11']
        else:
            cuncu['step_dic'] = [str(yyb) for yyb in cuncu['step_dic']]

        create_table()
        get_headers()
        global check_url
        check_url = f"http://online.gf.com.cn:8070/api/order/list?branchs={'%7C'.join(cuncu['yyb_dict'])}&company={'%7C'.join(cuncu['com_dic'])}&enableNotification=0&orderType=1&step={'%7C'.join(cuncu['step_dic'])}"
        print(check_url)#筛选订单
        # def check_order():
        #     while snatch_flag:
        # #         # test(cuncu['yyb_dict'],cuncu['com_dic'],cuncu['step_dic'])
        #         check(check_url)#筛选订单
        #         # time.sleep(intervl)
        # def snatch_order():
        #     #抢单
        #     while snatch_flag: 
        #         snatch()
                # time.sleep(0.001)#间隔频次影响日志大小，0.001大约1kb/分钟
        #Q:每次点击开始筛选就会创建一个新的子线程？？
        t1 = threading.Thread(target=quick_snatch)
        t1.start()

        t2 = threading.Thread(target=slow_snatch,args=(0.00001,))
        t2.start()

        t3 = threading.Thread(target=check,args=(check_url,0.0001))
        t3.start()

        # t4 = threading.Thread(target=slow_check,args=(0.09,check_url,))
        # t4.start()

        # t4 = threading.Thread(target=check_order)
        # t4.start()

        # t5 = threading.Thread(target=check_order)
        # t5.start()

    def stop(self):
        global snatch_flag,vartext,check_flag
        check_flag = False
        vartext.set('')
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}关闭筛选')

    def commit(self):
        global cuncu, vartext
        key = list(self.box_Vars.keys())[0]
        temp = []
        for i in range(len(self.box_Vars[key])):
            for j in range(len(self.box_Vars[key][i])):
                checked = self.box_Vars[key][i][j].get()
                if checked:
                    temp.append(checked)
        cuncu[key] = temp
        print(f"提交后cuncu{cuncu}")


def fram(dic,master,boxkey):
    #将分公司、营业部、审核类型字典均匀布局到界面中
    '''
    dic 分公司/营业部/审核类型字典
    '''
    global cuncu
    columns=5
    rows=math.ceil(len(list(dic.keys()))/columns)
    boxes = []
    boxVars = {boxkey:[]}
    dic_list = []
    #将字典键值生成二维数组
    for i in range(rows):
        boxVars[boxkey].append([])
        dic_list.append([])
        for j in range(columns):
            boxVars[boxkey][i].append(tkinter.IntVar())
            boxVars[boxkey][i][j].set(0)
            if i*columns+j < len(dic):
                dic_list[i].append(list(dic.keys())[i*columns+j])
            else:
                dic_list[i].append('')
    #根据二维左边生成勾选排列并相应填入字典键值二维数组
    for x in range(rows):
        boxes.append([])
        for y in range(columns):
            if dic_list[x][y] == '':
                continue
            # boxes[x].append(tkinter.Checkbutton(master,text = dic_list[x][y], onvalue=int(dic[dic_list[x][y]]),offvalue=0,variable = boxVars[x][y],command=selection(int(dic[dic_list[x][y]])).jia))
            boxes[x].append(tkinter.Checkbutton(master,text = dic_list[x][y], onvalue=int(dic[dic_list[x][y]]),offvalue=0,variable = boxVars[boxkey][x][y]))
            boxes[x][y].grid(row=x+2, column=y+2)
    button2 = tkinter.Button(master,text=' 确认选择 ',width=7,command=selection('',boxVars).commit)
    button2 . grid(row=x+3, columnspan=y+3)


def buju(mas):
    global cuncu, vartext
    entry1 = tkinter.Label(mas, width=120, height=3, bg='white', anchor='se', textvariable=vartext)
    entry1.grid(row=0, columnspan=5)
    frame1 = Frame (mas, relief=RAISED, borderwidth=2)
    frame1 . grid(row=1, columnspan=5)
    fram(yyb_dict,frame1,'yyb_dict')
    frame2 = Frame (mas, relief=RAISED, borderwidth=2)
    frame2 . grid(row=2, columnspan=5)
    fram(com_dic,frame2,'com_dic')
    frame3 = Frame (mas, relief=RAISED, borderwidth=2)
    frame3 . grid(row=3, columnspan=5)
    fram(step_dic,frame3,'step_dic')
    button1=tkinter.Button(mas,text=' 开启筛选 ',width=7,command=lambda : selection('','').start())
    button1 . grid(row=4, columnspan=5)
    button1=tkinter.Button(mas,text=' 关闭筛选 ',width=7,command=lambda : selection('','').stop())
    button1 . grid(row=5, columnspan=5)



buju(root)
root.mainloop()


# while True:
#     # input("请选择指定营业部")
#     check_num = check()#筛选订单
#     if check_num:#筛选到订单数不为0
#         order = []#初始化订单列表
#         for num in range(check_num):#根据筛选订单数进行循环
#             have_order = snatch()#抢单
#             if have_order:#抢到单
#                 order.append(have_order)#将订单内容添加到订单列表
#             if len(order) >= 10:#抢满10单进入下一轮筛选抢单
#                 break
#         print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}抢到{len(order)}单：{order}')
#     else:
#         print("没有单")
#         time.sleep(10)