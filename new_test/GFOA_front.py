from socket import socket,AF_INET,SOCK_STREAM
import os,sys,subprocess,time
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor

import GFOA_OP
import tkinter

from utils import tk_front
from utils.log_record import logger


def taskkill(port):
    # 杀死原有的进程
    for i in [port]:
        with os.popen('netstat -aon|findstr "{}"|findstr LISTENING'.format(i)) as p:
            lines = p.read().split("\n")
            for line in lines:
                if "LISTENING" in line:
                    pid = line[line.index("LISTENING") + 9:].strip()
                    os.system("taskkill -pid {} -f".format(pid))


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
    # p1.terminate()
    p2.terminate()
    p3.terminate()
    p4.terminate()
    # 关闭进程池
    # executor.shutdown()
    # 退出 tkinter 程序
    root.destroy()


######################backend######################
import json

def echo_handler(address,client_sock:socket,flag,vartext:tkinter.StringVar,share_list):
    #处理客户端连接
    logger.info('Got connection from {}'.format(address))
    try:
        msg = client_sock.recv(8192)
        cont = msg.decode('utf8')
        if "开始抢单" in cont:
            resend = '开始抢单成功'
            client_sock.sendall(resend.encode('utf8'))
            data = json.loads(cont.replace("开始抢单",""))
            share_list.append(data)
            logger.info(f"开始抢单数据{data}")
            
            flag.value = True
        elif "暂停抢单" in cont:
            flag.value = False
            resend = '暂停抢单成功'
            client_sock.sendall(resend.encode('utf8'))
            vartext.set('')
        elif '登录失效' in cont:
            flag.value = False
            vartext.set(cont)
            resend = f'暂停抢单成功,{cont}'
            client_sock.sendall(resend.encode('utf8'))
    except Exception as e:
        logger.info(f"后端socket消息异常:{e}")
    finally:
        client_sock.close()


def echo_server(address,flag,share_list,vartext,backlog=5):
    #启动socket服务端
    sock = socket(AF_INET,SOCK_STREAM)
    sock.bind(address)
    sock.listen(backlog)
    while True:
        client_sock,client_addr = sock.accept()
        logger.info("接收到监听")
        echo_handler(client_addr,client_sock,flag,vartext,share_list)

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

def check(flag,share_list,headers,port):
    while True:
        if flag.value:
            data = share_list[0]
            GFOA_OP.check(data['yyb_dict'],data['com_dic'],data['step_dic'],headers,port,flag)

def snatch(flag,headers,port):
    while True:
        if flag.value:
            for i in range(100):
                GFOA_OP.snatch(headers,port,flag)
            else:
                flag.value = False


if __name__ == "__main__":
    import multiprocessing
    from threading import Thread
    from multiprocessing import freeze_support
    freeze_support()
    #查询配置
    share_list = multiprocessing.Manager().list()
    #启停控制
    check_flag = multiprocessing.Value('b',False)
    snatch_flag = multiprocessing.Value('b',False)
    port = 20000
    taskkill(port)
    header = GFOA_OP.get_headers()
    p2 = multiprocessing.Process(target=check,args=[check_flag,share_list,header,port])
    p4 = multiprocessing.Process(target=check,args=[check_flag,share_list,header,port])
    p3 = multiprocessing.Process(target=snatch,args=[snatch_flag,header,port])
    
    p2.start()
    p3.start()
    p4.start()
    # with ThreadPoolExecutor(max_workers=2) as executor:
    #     app1 = executor.submit(echo_server,[('127.0.0.1',port),share_val])
    #     app2 = executor.submit(test,share_val)
    #     app3 = executor.submit(test,share_val)
    root=tkinter.Tk()
    vartext = tkinter.StringVar()
    t1 = Thread(target=echo_server,args=[('127.0.0.1',port),check_flag,share_list,vartext])
    t1.start()
    root.title('GFOA')
    root.resizable(0,0)
    tk_front.buju(root,port,vartext)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
