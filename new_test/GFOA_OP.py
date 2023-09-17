from utils.web_browser import specialBrowser
from utils import db_sql
import time,json,requests
from socket import socket,AF_INET,SOCK_STREAM
from utils.log_record import logger
import os
def con_server(ip:str,port:int):
    try:
        sock = socket(AF_INET,SOCK_STREAM)
        sock.connect((ip,port))
    except Exception as e:
        sock = None
        logger.info(f"连接服务端异常:{e}")
    finally:
        return sock

def send_msg(sock:socket,msg):
    try:
        sock.sendall(msg.encode("utf8"))
        data = sock.recv(1024)
        logger.info(f"后端请求收到消息{data.decode('utf8')}")
    except Exception as e:
        logger.info(f"后端请求消息异常:{e}")

def get_cookie():
    '''
    获取cookies并存入内置数据库
    '''
    try:
        db_sql.create_table()
        code_path = os.getcwd()
        chrome_path = rf'{code_path}\GoogleChrome\Chrome\chrome.exe'
        driver_path = rf'{code_path}\GoogleChrome\Chrome\chromedriver.exe'
        # driver_path = r"D:\工作\流程易\机器人V8.5.1\release\Python\python3_lib\chromedriver.exe"
        # chrome_path = r"D:\工作\流程易\机器人V8.5.1\release\Python\python3_lib\GoogleChrome\Chrome\chrome.exe"
        browser = specialBrowser(chromedriverPath=driver_path,chromepath=chrome_path)
        browser.get_url("http://online.gf.com.cn:8070/login")
        # browser.get("www.baidu.com")
        while True:
            try:
                login = browser.find_ele("//span[text()='抢']",retry=4)
                if login:
                    logger.info("登录成功")
                    break
            except Exception as e:
                pass
            time.sleep(2)
        cookie = browser.get_cookie()
        logger.info(f"获取到cookie:{cookie}")
        cookies={}
        for val in cookie:
            cookies[val['name']] = val['value']
        logger.info(f"拼凑cookies:{cookies}")
        insert_sql = f"INSERT INTO cookies Values ('{json.dumps(cookies)}','{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}','')"
        logger.info(db_sql.op_db(insert_sql))
    except Exception as e:
        logger.info(f"登录模块错误:{e}")
        cookies = {}
    finally:
        browser.close()
        return cookies

def get_headers():
    #通过数据库获取cookie,如果数据库没有则登录系统获取
    try:
        db_sql.create_table()
        headers = {}
        select_sql = 'select cookies from cookies where invalid_time = ""'
        cookies = db_sql.op_db(select_sql)
        if len(cookies)>0:
            logger.info(f"从数据库查询到cookie：{cookies}")
            #cookies:[(),()]
            cookie = json.loads(cookies[0][0])
        else:
            cookie = get_cookie()
            logger.info(f"从网页获取到cookie：{cookie}")
        headers['Cookie'] = f"sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%223073538%22%2C%22\
                            first_id%22%3A%2217f45ec7f5ec68-0815ae60ce6d35-4e607a6f-2304000-17f45ec7f5f409%22%2C%22%24\
                            device_id%22%3A%2217f799926ed2d-0958a2610ff164-56171d5e-2304000-17f799926ee1065%22%7D;\
                            JSESSIONID={cookie['JSESSIONID']}; SECKEY_ABVK={cookie['SECKEY_ABVK']}; BMAP_SECKEY={cookie['BMAP_SECKEY']};\
                            token={cookie['token']}"
        logger.info(f"拼凑得到新header：{headers}")
    except Exception as e:
        logger.info(f"合成header错误:{e}")
    finally:
        return headers

def check(branch,company,step,headers,port,flag):
    try:
        #筛选所有分公司营业部订单
        url = f"http://online.gf.com.cn:8070/api/order/list?branchs={'%7C'.join(branch)}&company={'%7C'.join(company)}&enableNotification=0&orderType=1&step={'%7C'.join(step)}"
        payload={}
        response = requests.request("GET", url, headers=headers, data=payload)
        #响应示例
        #{"code":0,"data":[{"orderType":1,"orderId":"632ae40c656ece6e8e308cdc","customerId":null,"branchName":"广州花都紫薇路营业部","step":4.0,"remainTime":119321,"customerName":"黄清宁","expiredTime":"2022-09-23 08:30:00","branchNo":"313"}],"msg":"筛选订单成功！"}
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if response.status_code == 200:
            cont = json.loads(response.text)
            if cont['msg'] == '筛选订单成功！':
                logger.info(f'({time.time()}){cont["msg"]},共{len(cont["data"])}单,{cont["data"]}')
            #     # order_num = len(cont["data"])
            #     # if order_num > 0:
            #     #     order = []#初始化订单列表
            #     #     for i in range(order_num):#根据筛选订单数进行循环
            #     #         have_order = snatch_order()#抢单
            #     #         if have_order:#抢到单
            #     #             order.append(have_order)#将订单内容添加到订单列表
            #     #     logger.info(f'{start_time}抢到{len(order)}单：{order}')
            else:
                if int(start_time[17:19]) % 30 == 0:#每20秒打印一次(以便抽查频率)
                    logger.info(f'({time.time()}){cont["msg"]}')
        else:
            logger.info(f'请求异常：{response.status_code}')
            db_sql.clear_cookie()
            raise Exception(f'请求异常：{response.status_code}')
    except Exception as e:
        logger.info(f"筛选请求异常:{str(e)}")
        if "请求异常" in str(e):
            so = con_server('127.0.0.1',port)
            send_msg(so,'登录失效，请重启软件进行登录')
            flag.value = False


def snatch(headers,port,flag):
    try:
        #抢单
        # headers['User-Agent'] = faker.user_agent()
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        url = "http://online.gf.com.cn:8070/api/order/snatch"
        payload = "{}"
        #响应示例
        #{"code":0,"data":{"orderType":1,"orderId":"632ae40c656ece6e8e308cdc","customerId":null,"branchName":"广州花都紫薇路营业部","step":4.0,"remainTime":1799,"customerName":"黄清宁","expiredTime":"2022-09-23 08:30:00","branchNo":"313"},"msg":"抢单成功！"}
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            cont = json.loads(response.text)
            if cont['msg'] == '抢单成功！':
                logger.info(f'({time.time()}){cont["msg"]}{cont["data"]}')
                #单独抢时注释
                # flag.value = False
            else:
                if int(start_time[17:19]) % 30 == 0:#每20秒打印一次(以便抽查频率)，同时控制日志大小
                    if cont["msg"] == '操作太过频繁':
                        logger.info(f'({time.time()})')
                    else:
                        logger.info(f'({time.time()}){cont["msg"]}')
        else:
            logger.info(f'({time.time()})请求异常：{response.status_code}')
            db_sql.clear_cookie()
            raise Exception(f'({time.time()})请求异常：{response.status_code}')
    except Exception as e:
        logger.info(f"({time.time()})抢单请求异常:{str(e)}")
        if "请求异常" in str(e):
            so = con_server('127.0.0.1',port)
            send_msg(so,'登录失效，请重启软件进行登录')
            flag.value = False
