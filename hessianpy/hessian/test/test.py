# -*- coding: UTF-8 -*-
#
# Hessian protocol implementation test
#
# Protocol specification can be found here
# http://www.caucho.com/resin-3.0/protocols/hessian-1.0-spec.xtp
#
# This file contains some tests for HessianPy library.
#
# Copyright 2005 Petr Gladkikh (batyi at mail ru)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
from hessian.hessian import *
from hessian.client import *
from hessian.server import HessianHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from StringIO import StringIO
from time import time
import traceback
from threading import Thread


__revision__ = "$Rev$"

    
def loopBackTest(classRef, value):
    s = StringIO()
    o = classRef()
    o.write(WriteContext(s), value)
    # print "[" + s.data + "]" # debug
    s.seek(0)
    r = readObject(ParseContext(s))
    res = False
    try:
        res = r == value
    except RuntimeError, e:
        # fallback in case of recusion error
        res = `r` == `value`
        
    assert res


def loopBackTestTyped(classRef, value, converter = None):
    """ This test is for objects with ambiguous type prefixes,
    'converter' is used for types that are not preserved after
    serialization
    """
    s = StringIO()
    o = classRef()
    o.write(WriteContext(s), value)
    # print "T[" + s.data + "]" # debug
    s.seek(0)
    s_in = ParseContext(s)
    if converter != None:
        value = converter(value)
    assert o.read(s_in, s_in.read(1)) == value


def loopbackTest():
    loopBackTest(hessian.Null, None)
    loopBackTest(Bool, True)
    loopBackTest(Bool, False)    
    loopBackTest(Int, 12343)
    loopBackTest(Long, 2403914806071207089L)
    loopBackTest(Double, 0.0)
    loopBackTest(Double, 123.321)
    loopBackTest(String, "")
    loopBackTest(String, "Nice to see ya!")
    loopBackTest(Binary, "\x07Nice to see ya! )*)(*РєР°РјРїСѓС‚РµСЂ&)(*\x00&)(*&)(*&&*\x09^%&^%$%^$%$!#@!")
    loopBackTest(Array, [])
    loopBackTest(Array, ["123", 1])
    loopBackTest(Array, [3, 3])
    loopBackTest(Array, [None, [3]])
    loopBackTest(Array, [[[3]]])
    loopBackTest(Map, {})
    loopBackTest(Map, {1 : 2})
    loopBackTest(Remote, RemoteReference("yo://yeshi/yama"))
    loopBackTestTyped(Xml, u"<hello who=\"Небольшой текст тут!\"/>")
    
    loopBackTestTyped(Tuple, (), list)
    loopBackTestTyped(Tuple, (1,), list)
    loopBackTestTyped(Tuple, ("equivalence", 1, {"":[]}), list)    


def serializeCallTest():    
    loopBackTest(Call, ("aaa", [], []))
    loopBackTest(Call, ("aaa", [], [1]))
    loopBackTest(Call, ("aaa", [], ["ddd", 1]))
    loopBackTest(Call, ("aaa", [("type", 1)], []))
    loopBackTest(Call, ("aaa", [("type", "isolated")], [23]))
    loopBackTest(Call, ("aaa", [], \
                        [{"name" : "beaver", "value" : [987654321, 2, 3.0] }]))


def serializeReplyTest():    
    loopBackTestTyped(Reply, ([], True, 1))
    loopBackTestTyped(Reply, ([], True, {"code" : [1, 2]}))
    loopBackTestTyped(Reply, ([], False, {}))
    loopBackTestTyped(Reply, ([], False, {"code" : "value"}))


def referenceTest():
    m = {"name" : "beaver", "value" : [987654321, 2, 3.0] }
    loopBackTest(Call, ("aaa", [], [m, m]))
    a = [1, 2, 3]
    a[2] = a
    loopBackTest(Call, ("aaa", [], [a]))
    b = [a, 1]
    a[0] = b
    loopBackTest(Call, ("aaa", [], [b, a]))


# ---------------------------------------------------------
# remote call tests


SECRET_MESSAGE = "Hello, from HessianPy!"
TEST_PORT = 7777


def warnConnectionRefused(exception, url):
    if exception.args == (10061, 'Connection refused') \
        or exception.args == (11001, 'getaddrinfo failed'):
        print "\nWarning: Server '" + url +  "'is not available. Can not perform a callTest"
        return True
    else:
        return False


class TestHandler(HessianHTTPRequestHandler):   

    OTHER_PREFIX = "somewhere"
    
    def nothing():
        pass
    
    def hello():
        return SECRET_MESSAGE
    
    def echo(some):
        return some
        
    def askBitchy():
        raise Exception("Go away!")
    
    def redirect(home_url):
        return hessian.RemoteReference(home_url + TestHandler.OTHER_PREFIX)
    
    def sum(a, b):
        return a + b
    
    message_map = {
                   "nothing" : nothing, 
                   "hello" : hello, 
                   "askBitchy" : askBitchy, 
                   "echo" : echo, 
                   "redirect" : redirect, 
                   "sum" : sum }


class TestServer(Thread):    
    def run(self):
        print "\nStarting test HTTP server"
        server_address = ('localhost', TEST_PORT)
        httpd = HTTPServer(server_address, TestHandler)
        print "Serving from ", server_address
        httpd.serve_forever()


def callBlobTest(proxy):    
    size = 2**17
    big = "*" * size
    r = proxy.echo(big)
    assert big == r
    
    
def redirectTest(proxy):
    proxy2 = proxy.redirect(proxy.url)
    s = proxy2.sum(654321, 123456)
    assert s == 777777
    
    p = proxy    
    for k in range(3): p = p.echo(p)
    assert p.hello() == SECRET_MESSAGE
  

def callTestLocal(url):
    srv = TestServer()
    srv.setDaemon(True)
    srv.start()
    
    proxy = HessianProxy(url)
        
    msg = proxy.nothing()
    assert None == msg
      
    msg = proxy.hello()
    assert SECRET_MESSAGE == msg    
        
    try:
        proxy.askBitchy()
        assert False # should not get here
    except Exception, e:
        # print traceback.format_exc() # debug
        pass    
    
    # What about UTF-8?
    padonkRussianMessage = u"Пррревед абонентеги!"
    assert padonkRussianMessage == proxy.echo(padonkRussianMessage)
    
    callBlobTest(proxy)
    redirectTest(proxy)
        
    if False:
        print "Some performance measurements..."
        count = 500
        start = time()
        for i in range(count):
            proxy.hello()
        fin = time()
        print "One call takes", 1000.0 * (fin - start) / count, "mSec."        
        
    # TODO: How can we kill server while it's waiting on socket?
    srv = None    


def callTestPublic(url):
    try:
        proxy = HessianProxy(url)
        
        proxy.nullCall()
        # In the next moment nothing continued to happen.
        
        assert "Hello, world" == proxy.hello()
        print '.', 
        
        o = {1:"one", 2:"two"}
        assert o == proxy.echo(o)
        print '.', 
        
        o = (-1, -2)
        assert list(o) == proxy.echo(o)
        print '.', 
        
        o = ["S-word", "happen-s"]
        assert o == proxy.echo(o)
        print '.', 
        
        a, b = 1902, 34
        assert (a - b) == proxy.subtract(a, b)
        print '.', 
        
        # What about UTF-8?
        padonkRussianMessage = u"Превед!"
        assert padonkRussianMessage == proxy.echo(padonkRussianMessage)
        print '.', 
                                                                                  
    except Exception, e:
        st = traceback.format_exc()
        if not warnConnectionRefused(e, url):
            print st
            raise e # re-thow


def sslTest():
    try:
        import OpenSSL
    except Exception, e:
        print "Warning: No OpenSSL module. SSL will not be tested."
        return
    
    import testSecure
    testSecure.testHttps()
     

if __name__ == "__main__":
    try:
        loopbackTest()
        print '.', 
        serializeCallTest()
        print '.', 
        serializeReplyTest()
        print '.', 
        referenceTest()
        print '.', 
        
        callTestLocal("http://localhost:%d/" % TEST_PORT)
        sslTest()
        callTestPublic("http://www.caucho.com/hessian/test/basic")        
        
        print "\nTests passed."
        
    except Exception, e:
        st = traceback.format_exc()
        print "\nError occured:\n", st
