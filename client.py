#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from escpos import *
import time

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect


def escprint(content):
    usb._raw('\x1b\x40')
    usb.text(content.encode('gbk'))
    usb._raw('\x0a')

class Client(object):
    def __init__(self, url, timeout, uuid):
        self.uuid = uuid
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect()
        PeriodicCallback(self.keep_alive, 20000, io_loop=self.ioloop).start()
        self.ioloop.start()

    @gen.coroutine
    def connect(self):
        print "trying to connect"
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception, e:
            print "connection error: %s" % e
        else:
            #连接服务器成功，注册此设备
            print "connected"
            self.ws.write_message(json.dumps({"type": "register", "uuid": self.uuid}))
            self.run()

    @gen.coroutine
    def run(self):
        while True:
            msg = yield self.ws.read_message()
            if msg is None:
                print "connection closed"
                self.ws = None
                break
            else:
                print "client received: %s" % msg
                message = json.loads(msg)
                if message["type"] == "print":
                    try:
                        escprint(message["content"])
                        result = True

                    except:
                        print "print failed"
                        result = False

                    self.ws.write_message(json.dumps({"type": "print_done",
                                                      "uuid": self.uuid,
                                                      "cmd_uuid": message["cmd_uuid"],
                                                      "result": result}))
                else:
                    pass


    def keep_alive(self):
        if self.ws is None:
            self.connect()
        else:
            self.ws.write_message(json.dumps({"type": "keep_alive"}))


if __name__ == "__main__":
    while True:
        try:
            usb = printer.Usb(0x0416, 0x5011, 0, out_ep=0x01)
            break
        except AttributeError:
            time.sleep(5)

    client = Client("ws://lespark.us:8080/ws", 5, "raspberry_pi")