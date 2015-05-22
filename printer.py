# coding=utf-8
from escpos import *
usb = printer.Usb(0x0416, 0x5011, 0, out_ep=0x01)

usb._raw('\x1b\x40')
usb.set(font='a', type='b', align='center', width=2, height=2)
usb.text(u"LesPark 拉拉公园\n\n".encode('gbk'))
usb.set()
usb.text(u"陪领导打麻将，领导无意中说：我最欣赏蒋介石，宋美龄喜欢梧桐，蒋介石就在南京种满了梧桐。我心领神会，打出一张五筒，领导：胡。\n\n".encode("gbk"))
usb.image('logo.png')
usb.qr('http://ad.lespark.us/?m=download')
usb._raw('\x0a')
# usb.set(codepage=None, align='center')#设置页面居中

# usb.cut()#切纸
