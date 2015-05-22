# coding=utf-8
import json
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

from tornado.options import define, options

define("port", default=8080, help="run on the given port", type=int)

all_client_dict = {}


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", clients=all_client_dict.keys(), server="lespark.cn:8080")


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        """客户端连接上了服务器, 发送欢迎消息"""
        print 'new connection'
        # self.write_message("server: accept a new connection")

    def on_message(self, message):
        # print 'message received %s' % message
        try:
            msg = json.loads(message)
        except Exception as e:
            msg = None

        if msg is None:
            return False

        if msg["type"] == "register":
            # 新客户端连接上服务器
            all_client_dict[msg["uuid"]] = self
        elif msg["type"] == "keep_alive":
            pass
        elif msg["type"] == "print_cmd":
            # 让某个客户端打印消息
            client_uuid = msg["client_uuid"]
            content = msg["content"]

            try:
                all_client_dict[client_uuid].write_message(json.dumps({"type": "print",
                                                                       "content": content,
                                                                       "cmd_uuid": msg["uuid"]}))
            except:
                if client_uuid in all_client_dict:
                    del all_client_dict[client_uuid]

        elif msg["type"] == "print_done":
            # 客户端打印, 通知发送命令者成功或者失败
            all_client_dict[msg["cmd_uuid"]].write_message(json.dumps({"type": "print_result",
                                                                "uuid": msg["uuid"],
                                                                "result": msg["result"]}))
        elif msg["type"] == "logout":
            del all_client_dict[msg["uuid"]]


    def on_close(self):
        print 'server: connection closed'


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/", IndexHandler),
            (r"/ws", WebSocketHandler)
        ]
    )
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(options.port)
    print "Listening on port:", options.port
    tornado.ioloop.IOLoop.instance().start()