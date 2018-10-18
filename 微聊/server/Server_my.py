# coding:utf-8
import socketio,eventlet,random
import pickle
import os

# 实例化io对象
sio = socketio.Server()
# 定义两个房间
clientDict = {
    'pythonRoom':{'sid':'pythonRoom','name':'Python群聊%s'%random.randint(10000,99999),'imgUrl':'http://wx1.sinaimg.cn/orj360/006pnLoLgy1ft6yichmarj30j60j675x.jpg','signature':'这个人很懒！','isRoom':True},
    'javaRoom':{'sid':'javaRoom','name':'java群聊%s'%random.randint(10000,99999),'imgUrl':'http://wx1.sinaimg.cn/orj360/006pnLoLgy1ft6yichmarj30j60j675x.jpg','signature':'这个人很懒！','isRoom':True}
}
data1 =[]

n=1
# 开始事件的监听函数
@sio.on('connect')
def connect(sid,environ):
    global n,clientDict
    if os.path.exists('info.json'):
        with open('info.json','rb') as f:
            clientDict = pickle.load(f)

    if not hasattr(clientDict,sid):
        clientDict[sid] = {'sid':sid,'name':'客户%s'%n,'imgUrl':'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1539518159057&di=7f3f846456ba019ea06f30f09f4b7505&imgtype=0&src=http%3A%2F%2Fimg.mp.itc.cn%2Fupload%2F20161027%2F9769626c447642c48dd4f9600e54a6ee_th.jpeg','signature':'这个人很懒！','isRoom':False}
    sio.emit('updateDict',clientDict)
    sio.emit('emiteID',sid,room=sid)
    # print('connect', sid,clientDict)
    n+=1

    with open('info.json','wb') as f:
        pickle.dump(clientDict,f)
    print('保存成功')

# 两个人之间的私信
@sio.on('sendMsg')
def sendMsg(sid,data):
    data['srcimg'] = clientDict[data['srcId']]['imgUrl']
    # data['destimg'] = clientDict[data['destId']]['imgUrl']
    data['srcname'] = clientDict[data['srcId']]['name']
    data['isRoom'] = clientDict[data['destId']]['isRoom']
    # data['destname'] = clientDict[data['destId']]['name']
    # data['nums'] = 0

    sio.emit('reply',data,room=data['destId'],skip_sid=data['srcId'])
    sio.emit('reply',data,room=data['srcId'])
    print('微聊',data)



# 进入qun聊天
@sio.on('enterRoom')
def enterRoom(sid, data):
    print(sid,data['room'])
    sio.enter_room(sid, data['room'])
    info = {'content': '欢迎%s进入房间' % sid, 'destId': sid, 'srcId': '系统提示','srcimg':clientDict[sid]['imgUrl']}
    sio.emit('reply', info, room=data['room'])

# 离开qun聊天
@sio.on('leaveRoom')
def leaveRoom(sid, data):
    sio.leave_room(sid, data['room'])
    info = {'content': '%s离开房间' % sid, 'destId': sid, 'srcId': '系统提示'}
    sio.emit('reply', info, room=data['room'])


#创建群聊
@sio.on('createRoom')
def createRoom(sid,data):

    clientDict[data['room']] = {'sid': data['room'], 'name': 'c语言程序设计','imgUrl': 'http://wx1.sinaimg.cn/orj360/006pnLoLgy1ft6yichmarj30j60j675x.jpg','signature': '这个人很懒！', 'isRoom': True}
    sio.emit('updateDict', clientDict)


@sio.on('editText')
def editText(sid,data):
    print('数据：',data)
    if len(data['name'])!=0:
        clientDict[data['sid']]['name'] = data['name']
    if len(data['imgUrl'])!=0:
        clientDict[data['sid']]['imgUrl'] = data['imgUrl']
    if len(data['sig'])!=0:
        clientDict[data['sid']]['signature'] = data['sig']
    sio.emit('updateText',clientDict)

    print('成功更新列表',clientDict)

    with open('info.json','wb') as f:
        pickle.dump(clientDict,f)
    print('保存成功')


@sio.on('disconnect')
def disconnect(sid):
    # print('disconnect ', sid)
    clientDict.pop(sid)  # 如果客户端断开连接，那么将客户端从clientList客户端列表删除
    sio.emit('updateClients', clientDict)  # 告诉前端更新一下，在线好友（客户端列表）




# 开始跑这个服务
if __name__=='__main__':
    if os.path.exists('info.json'):
        with open('info.json','rb') as f:
            clientDict = pickle.load(f)
    # sio通过middleware转为应用服务
    app = socketio.Middleware(sio)
    # 依赖event网关服务器
    eventlet.wsgi.server(eventlet.listen(('',8080)),app)

