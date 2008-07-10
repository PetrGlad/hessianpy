# -*- coding: UTF-8 -*-
#
# Hessian protocol implementation test
#
# Protocol specification can be found here
# http://hessian.caucho.com/doc/hessian-1.0-spec.xtp
#
# This file contains some tests for HessianPy library.
#
# Copyright 2005 Petr Gladkikh (batyi at users sourceforge net)
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
from hessian.server import HessianHTTPRequestHandler, StoppableHTTPServer
from StringIO import StringIO
from time import time
from threading import Thread
import traceback
import urllib2


__revision__ = "$Rev$"


def readObjectString(txt):
    stream = StringIO(txt)
    return readObjectByPrefix(ParseContext(stream), stream.read(1))


def parseData(txt):
    """Auxiliary function.
    Takes plain text description of binary data 
    from protocol specification and returns binary data"""
    import re
    result = ""
    for a in re.split('\s+', txt):
        if re.match('x[0-9a-f]{2}', a, re.IGNORECASE):            
            result += chr(int(a[1:], 16))
        else:
            result += a    
    return result


def autoLoopBackTest(value):
    s = StringIO()
    writeObject(WriteContext(s), value, None)    
    s.seek(0)    
    r = readObjectByPrefix(ParseContext(s), s.read(1))
    assert r == value
        
    
def loopBackTest(classRef, value):
    s = StringIO()
    o = classRef()
    o.write(WriteContext(s), value)
    s.seek(0)
    r = readObject(ParseContext(s))
    res = False
    try:
        res = r == value
    except RuntimeError, e:
        # Fall-back in case of recursion error
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
    loopBackTest(UnicodeString, u"")
    loopBackTest(UnicodeString, u"Nice to see ya! длорфызвабьйтцуикзгшщчсмжячмс.")
    loopBackTest(UnicodeString, "Nice to see ya!")
    loopBackTest(Array, [])
    loopBackTest(Array, ["123", 1])
    loopBackTest(Array, [3, 3])
    loopBackTest(Array, [None, [3]])
    loopBackTest(Array, [[[3]]])
    loopBackTest(Map, {})
    loopBackTest(Map, {1 : 2})
    loopBackTest(Remote, RemoteReference("yo://yeshi/yama"))
        
    loopBackTestTyped(Tuple, (), list)
    loopBackTestTyped(Tuple, (1,), list)
    loopBackTestTyped(Tuple, ("equivalence", 1, {"":[]}), list)
    
    autoLoopBackTest(
        u"\x07Nice to see ya! )*)(*РєР°РјРїСѓС‚РµСЂ&)(*\x00&)(*&)(*&&*\x09^%&^%$%^$%$!#@!")
    autoLoopBackTest(
        "\x07Nice to see ya! )*)(*РєР°РјРїСѓС‚РµСЂ&)(*\x00&)(*&)(*&&*\x09^%&^%$%^$%$!#@!")
    
   
def testHessianTypes():    
    autoLoopBackTest(XmlString(u"<hello who=\"Небольшой текст тут!\"/>"))    
    

def serializeCallTest():    
    loopBackTest(Call, ("aaa", [], []))
    loopBackTest(Call, ("aaa", [], [1]))
    loopBackTest(Call, ("aaa", [], ["ddd", 1]))
    loopBackTest(Call, ("aaa", [("type", 1)], []))
    loopBackTest(Call, ("aaa", [("headerName", "headerValue")], [23]))
    loopBackTest(Call, ("aaa", [("headerName", "headerValue"), 
                               ("headerName2", "headerValue2")], [23]))
    loopBackTest(Call, ("aaa", [], \
                        [{"name" : "beaver", "value" : [987654321, 2, 3.0] }]))


def serializeReplyAndFaultTest():    
    loopBackTestTyped(Reply, ([], True, 1))
    loopBackTestTyped(Reply, ([], True, {"code" : [1, 2]}))
    loopBackTestTyped(Reply, ([], False, {}))
    loopBackTestTyped(Reply, ([], False, {"code" : "value"}))
    
    loopBackTestTyped(Reply, ([("headerName", "headerValue")], True, 33))
    loopBackTestTyped(Reply, ([("headerName", "headerValue"), 
                               ("headerName2", "headerValue2")], True, 33))
    
    loopBackTestTyped(Fault, {"message":"an error description", "line":23})


def referenceTest():
    m = {"name" : "beaver", "value" : [987654321, 2, 3.0] }
    loopBackTest(Call, ("aaa", [], [m, m]))
    a = [1, 2, 3]
    a[2] = a
    loopBackTest(Call, ("aaa", [], [a]))
    b = [a, 1]
    a[0] = b
    loopBackTest(Call, ("aaa", [], [b, a]))

    
def deserializeTest():
    txt = """V t x00 x03 int
      l x00 x00 x00 x02
      I x00 x00 x00 x00
      I x00 x00 x00 x01
      z"""      
    assert(readObjectString(parseData(txt)), [0, 1])
    
    txt = """V 
      l xff xff xff xff
      I x00 x00 x00 x00
      I x00 x00 x00 x01
      I x00 x00 x00 x03
      z"""      
    assert(readObjectString(parseData(txt)), [0, 1, 3])


# ---------------------------------------------------------
# remote call tests


SECRET_MESSAGE = "Hello from HessianPy!"
TEST_PORT = 7777


def warnConnectionRefused(exception, url):    
    print "\nException:", exception
    # If 'Connection refused' or 'getaddrinfo failed'
    if (hasattr(exception, "args") and exception.args[0] in [11001, 10061]) \
        or(hasattr(exception, "args") and exception.reason[0] in [11001, 10061]):
        print "Warning: Server '" + url +  "'is not available. Can not perform a remote call test."
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
        self.httpd = StoppableHTTPServer(server_address, TestHandler)
        print "Serving from ", server_address
        self.httpd.serve()
        
    def stop(self):
        self.httpd.stop()


def callBlobTest(proxy):    
    size = 2**11
    big = u"ЦЦ*муха" * size
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
    padonkMessage = u"Пррревед обонентеги!"
    assert padonkMessage == proxy.echo(padonkMessage)
    
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

    srv.stop()
    proxy.nothing() # XXX force accept loop so thread exits sooner :)


def realWorldTest1():
    import zlib, pickle     
    payload = zlib.compress(pickle.dumps("blah blah blah"))
    autoLoopBackTest(payload)


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
    
    import hessian.test.testSecure
    hessian.test.testSecure.testHttps()
     
def runList(funList):
    for fn in funList:
        fn()
        print '.',

if __name__ == "__main__":
    try:
        runList([
                 deserializeTest,
                 loopbackTest,
                 serializeCallTest,
                 testHessianTypes, 
                 serializeReplyAndFaultTest, 
                 referenceTest, 
                 realWorldTest1,
                 lambda: callTestLocal("http://localhost:%d/" % TEST_PORT),
                 sslTest
                 ])
        
        print "Warning: Test with public service is disabled."
        # Following URL seems to be unavailable anymore
        # callTestPublic("http://www.caucho.com/hessian/test/basic/")
        
        print "\nTests passed."
        
    except Exception, e:
        st = traceback.format_exc()
        print "\nError occured:\n", st
