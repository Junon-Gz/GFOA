from socket import socket,AF_INET,SOCK_STREAM
import os,sys,subprocess,time
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor

import GFOA_OP
import tkinter

from utils import tk_front
from utils.log_record import logger
import psutil

def check_port(ports:list[int]) ->int:
    # 检查端口是否被占用
    sock = socket(AF_INET, SOCK_STREAM)
    for port in ports:
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            # 端口被占用，查找占用该端口的进程并终止它
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr.port == port:
                    proc = psutil.Process(conn.pid)
                    #获取占用端口的pid的进程名称
                    process_name = proc.name()
                    logger.info(f"Port {port} is already in use by process {process_name} PID {conn.pid}. ")
                    if 'GFOA' in  process_name:
                        logger.info("Killing the process...")
                        try:
                            proc.terminate()
                            proc.wait()
                            logger.info(f"Process with PID {conn.pid} terminated.")
                            logger.info(f"use Port {port}")
                            return port
                        except psutil.NoSuchProcess:
                            logger.info(f"Process with PID {conn.pid} does not exist.")
                    else:
                        break
        else:
            logger.info(f"Port {port} is available.")
            logger.info(f"use Port {port}")
            return port


def net_is_used(port, ip='127.0.0.1'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.shutdown(2)
        # logger.info('%s:%d is used' % (ip,port))
        return True
    except:
        # logger.info('%s:%d is unused' % (ip,port))
        return False


def run_backend(port):
    sleepTimes = 0
    #启动服务端
    p_http = subprocess.Popen([sys.executable, "-u", os.path.dirname(__file__) + os.sep + "GFOA_backend.py" , "--port" , str(port)])
    while True:
        #检查服务端是否启动成功
        if net_is_used(port) or sleepTimes > 10:
            # logger.debug("APP后台启动成功")
            break
        else:
            # logger.debug("等待APP后台启动...%s" % sleepTimes)
            time.sleep(0.5)
            sleepTimes = sleepTimes + 1
    p_http.wait()

def on_closing():
    logger.info("进程池结束")
    p1.terminate()
    p2.terminate()
    # p3.terminate()
    # 关闭进程池
    # executor.shutdown()
    # 退出 tkinter 程序
    root.destroy()


######################backend######################
import json

def echo_handler(address,client_sock:socket,vartext:tkinter.StringVar,share_list,flag,headers,port):
    #处理客户端连接
    logger.info('Got connection from {}'.format(address))
    try:
        msg = client_sock.recv(8192)
        cont = msg.decode('utf8')
        if "筛选订单成功" in cont:
            GFOA_OP.check_snatch(headers,port,flag)
            resend = f'执行抢单成功'
            client_sock.sendall(resend.encode('utf8'))
        elif "暂停抢单" in cont:
            flag.value = False
            resend = '暂停抢单成功'
            client_sock.sendall(resend.encode('utf8'))
            share_list.pop(0)
            vartext.set('')
        elif '登录失效' in cont:
            # BUG:登录失效未能更新显示
            flag.value = False
            vartext.set(cont)
            resend = f'暂停抢单成功,{cont}'
            client_sock.sendall(resend.encode('utf8'))
        elif '开始抢单' in cont:
            resend = '开始抢单成功'
            client_sock.sendall(resend.encode('utf8'))
            data = json.loads(cont.replace("开始抢单",""))
            share_list.append(data)
            # BUG 失效时死锁(单抢需考虑其他替代方案)
            # GFOA_OP.check(data['order_type_dic'],data['yyb_dict'],data['com_dic'],data['step_dic'],headers,port,flag)
            logger.info(f"开始抢单数据{data}")
            flag.value = True

    except Exception as e:
        logger.info(f"后端socket消息异常:{e}")
    finally:
        client_sock.close()


def echo_server(address,port,flag,share_list,vartext,headers,backlog=5):
    try:
        #启动socket服务端
        sock = socket(AF_INET,SOCK_STREAM)
        sock.bind((address,port))
        sock.listen(backlog)
        while True:
            client_sock,client_addr = sock.accept()
            logger.info("接收到监听")
            echo_handler(client_addr,client_sock,vartext,share_list,flag,headers,port)
    except Exception as e:
        logger.info(f"服务端启动异常:{e}")

def test(flag):
    '''
    flag:启动/暂停抢单控制器(全局)
    '''
    #代替功能(抢单)函数
    while True:
        #开始/停止抢单控制器
        if flag.value:
            logger.info(time.time())
            for i in range(3):
                logger.info(i)
                time.sleep(2)

def check(check_flag,snatch_flag,share_list,headers,port):
    while True:
        if check_flag.value:
            data = share_list[0]
            GFOA_OP.check(data['order_type_dic'],data['yyb_dict'],data['com_dic'],data['step_dic'],headers,port,snatch_flag)

def snatch(snatch_flag,headers,port):
    #单独抢单调用常驻函数
    while True:
        if snatch_flag.value:
            GFOA_OP.snatch(headers,port,snatch_flag)


def check_snatch(snatch_flag,headers,port):
    #一边查一点抢调用常驻函数
    while True:
        if snatch_flag.value:
            GFOA_OP.check_snatch(headers,port,snatch_flag)

def socket_snatch(snatch_flag,headers,port):
    for i in range(100):
        GFOA_OP.check_snatch(headers,port,snatch_flag)


if __name__ == "__main__":
    import multiprocessing
    from threading import Thread
    from multiprocessing import freeze_support
    freeze_support()
    #共享(请求配置)列表
    share_list = multiprocessing.Manager().list()
    #启停控制
    check_flag = multiprocessing.Value('b',False)
    snatch_flag = multiprocessing.Value('b',False)
    ports = [i for i in range(18999,19000)]#常用端口号18999
    # BUG: 概率出现:1.原进程不能被kill会导致多端口占用
    port = check_port(ports)

    header = GFOA_OP.get_headers()

    #查+抢
    p1 = multiprocessing.Process(target=check,args=[check_flag,snatch_flag,share_list,header,port])
    p2 = multiprocessing.Process(target=check,args=[check_flag,snatch_flag,share_list,header,port])
    # # p3 = multiprocessing.Process(target=check_snatch,args=[snatch_flag,header,port])
    p1.start()
    p2.start()
    # p3.start()

    #单独抢
    # p1 = multiprocessing.Process(target=snatch,args=[snatch_flag,header,port])
    # p2 = multiprocessing.Process(target=snatch,args=[snatch_flag,header,port])
    # p1.start()
    # p2.start()

    # with ThreadPoolExecutor(max_workers=2) as executor:
    #     app1 = executor.submit(echo_server,[('127.0.0.1',port),share_val])
    #     app2 = executor.submit(test,share_val)
    #     app3 = executor.submit(test,share_val)
    root=tkinter.Tk()
    vartext = tkinter.StringVar()
    #查+抢
    t1 = Thread(target=echo_server,args=['127.0.0.1',port,check_flag,share_list,vartext,header])
    #单独抢
    # t1 = Thread(target=echo_server,args=['127.0.0.1',port,snatch_flag,share_list,vartext,header])
    t1.start()
    root.title('GFOA')
    root.resizable(0,0)
    tk_front.buju(root,port,vartext)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

