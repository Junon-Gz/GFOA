from tkinter import *
import tkinter
import time,math
import json
from socket import socket,AF_INET,SOCK_STREAM
from utils.log_record import logger
yyb_dict = {"广州天河路营业部":"301","广州黄埔大道营业部":"302","广州环市东路营业部":"303","广州花城大道营业部":"304","广州科韵路营业部":"305","广州中山三路中华广场营业部":"306","广州从化河滨南路营业部":"309","广州增城荔星大道营业部":"310","广州康王中路营业部":"311","广州黄埔东路营业部":"312","广州花都紫薇路营业部":"313","广州锦御一街营业部":"316","广州广州大道南营业部":"317","广州临江大道营业部":"318","广州农林下路营业部":"320","广州昌岗中路营业部":"367","广州江湾营业部":"369","广州洛溪新城营业部":"371","广州番禺环城东路营业部":"372","广州万博二路营业部":"373","广州宸悦路营业部":"378","广州黄埔大道中金融城营业部":"388","全部":"1"}
com_dic = {"广州花城大道美林基业大厦营业部":"308","广州寺右新马路营业部":"315","广州分公司":"7001","北京分公司":"7002","上海分公司":"7003","深圳分公司":"7004","东莞分公司":"7005","粤东分公司":"7006","佛山分公司":"7007","粤西分公司":"7010","江苏分公司":"7013","山东分公司":"7014","浙江分公司":"7015","河北分公司":"7016","湖北分公司":"7018","成都分公司":"7020","西安分公司":"7021","福建分公司":"7023","珠海分公司":"7025","海南分公司":"7027","长春分公司":"7028","辽宁分公司":"7029","全部":"1"}
step_dic = {"一审":"1","二审":"2","电话回访":"3","回访录音审核":"4","全部":"11"}
order_type_dic = {"证券开户（含下挂）":"1","纯基金开户":"8","港澳台开户":"9","全部":"1"}

class selection:

    
    def __init__(self,anjian,box_Vars):
        self.anjian = anjian
        self.box_Vars = box_Vars


    def start(self,port,vartext):
        #开始抢单按钮触发函数
        logger.info(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}开启筛选')
        if len(cuncu) == 0:
            pass
        else:
            logger.info(f"选择了{cuncu}")
            choose_order_type = [key for x in cuncu['order_type_dic'] for key,value in order_type_dic.items() if x == int(value)]
            choose_yyb = [key for x in cuncu['yyb_dict'] for key,value in yyb_dict.items() if x == int(value)]
            choose_com = [key for x in cuncu['com_dic'] for key,value in com_dic.items() if x == int(value)]
            choose_step = [key for x in cuncu['step_dic'] for key,value in step_dic.items() if x == int(value)]
            logger.info(f"选择业务类型：{','.join(choose_order_type)}\n选择营业部：{','.join(choose_yyb)}\n选择分公司：{','.join(choose_com)}\n选择审核类型：{','.join(choose_step)}")
            vartext.set(f"选择业务类型：{','.join(choose_order_type)}\n选择营业部：{','.join(choose_yyb)}\n选择分公司：{','.join(choose_com)}\n选择审核类型：{','.join(choose_step)}")
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
        
        if 11 in cuncu['order_type_dic']:
            cuncu['order_type_dic'] = [value for value in order_type_dic.values() if value != '11']
        else:
            cuncu['order_type_dic'] = [str(yyb) for yyb in cuncu['order_type_dic']]
        
        conn = self.con_server('127.0.0.1',int(port))
        self.send_msg(conn,"开始抢单"+json.dumps(cuncu))

    def stop(self,port):
        #暂停抢单按钮触发函数
        conn = self.con_server('127.0.0.1',int(port))
        self.send_msg(conn,"暂停抢单")
        logger.info(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}关闭筛选')

    def commit(self):
        #确认选择按钮触发函数
        global cuncu
        key = list(self.box_Vars.keys())[0]
        temp = []
        for i in range(len(self.box_Vars[key])):
            for j in range(len(self.box_Vars[key][i])):
                checked = self.box_Vars[key][i][j].get()
                if checked:
                    temp.append(checked)
        cuncu[key] = temp
        logger.info(f"提交后cuncu{cuncu}")

    def con_server(self,ip:str,port:int):
        try:
            sock = socket(AF_INET,SOCK_STREAM)
            sock.connect((ip,port))
        except Exception as e:
            sock = None
            logger.info(f"连接服务端异常:{e}")
        finally:
            return sock
    
    def send_msg(self,sock:socket,msg):
        try:
            sock.sendall(msg.encode("utf8"))
            data = sock.recv(1024)
            logger.info(f"前端收到消息{data.decode('utf8')}")
        except Exception as e:
            logger.info(f"前端消息异常:{e}")


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


def buju(mas,port,vartext:tkinter.StringVar):
    global cuncu
    cuncu = {'yyb_dict': [], 'com_dic': [], 'step_dic': [],'order_type_dic':[]}
    entry1 = tkinter.Label(mas, width=120, height=4, bg='white', anchor='se', textvariable=vartext)
    entry1.grid(row=0, columnspan=5)
    frame2 = Frame (mas, relief=RAISED, borderwidth=2)
    frame2 . grid(row=1, columnspan=5)
    fram(order_type_dic,frame2,'order_type_dic')
    frame3 = Frame (mas, relief=RAISED, borderwidth=2)
    frame3 . grid(row=2, columnspan=5)
    fram(yyb_dict,frame3,'yyb_dict')
    frame4 = Frame (mas, relief=RAISED, borderwidth=2)
    frame4 . grid(row=3, columnspan=5)
    fram(com_dic,frame4,'com_dic')
    frame5 = Frame (mas, relief=RAISED, borderwidth=2)
    frame5 . grid(row=4, columnspan=5)
    fram(step_dic,frame5,'step_dic')
    button1=tkinter.Button(mas,text=' 开启筛选 ',width=7,command=lambda : selection('','').start(port,vartext))
    button1 . grid(row=5, columnspan=5)
    button1=tkinter.Button(mas,text=' 关闭筛选 ',width=7,command=lambda : selection('','').stop(port))
    button1 . grid(row=6, columnspan=5)



if __name__ == "__main__":
    root=tkinter.Tk()
    root.title('GFOA')
    root.resizable(0,0)
    buju(root,20000)
    root.mainloop()