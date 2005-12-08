#
# Hessian protocol implementation
#
# Protocol specification can be found here
# http://www.caucho.com/resin-3.0/protocols/hessian-1.0-spec.xtp
#
# This file contains tests.
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
from hessian import *
from client import *
from StringIO import StringIO
from time import time

    
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


def loopBackTestTyped(classRef, value):
    "This test is for objects with ambiguous type prefixes"
    s = StringIO()
    o = classRef()
    o.write(WriteContext(s), value)
    # print "T[" + s.data + "]" # debug
    s.seek(0)
    s_in = ParseContext(s)
    assert o.read(s_in, s_in.read(1)) == value


def loopbackTest():
    loopBackTest(Null, None)
    loopBackTest(Bool, True)
    loopBackTest(Bool, False)    
    loopBackTest(Int, 12343)
    loopBackTest(Long, 2403914806071207089)
    loopBackTest(Double, 0.0)
    loopBackTest(Double, 123.321)
    loopBackTest(String, "")
    loopBackTest(String, "Nice to see ya!")
    loopBackTest(Binary, "Nice to see ya! )*)(*&)(*&)(*&)(*&&*^%&^%$%^$%$!#@!")
    loopBackTest(Array, [])
    loopBackTest(Array, ["123", 1])
    loopBackTest(Array, [3, 3])
    loopBackTest(Array, [None, [3]])
    loopBackTest(Array, [[[3]]])
    loopBackTest(Map, {})
    loopBackTest(Map, {1 : 2})


def serializeCallTest():
    loopBackTest(Call, ("aaa", [], []))
    loopBackTest(Call, ("aaa", [], [1]))
    loopBackTest(Call, ("aaa", [], ["ddd", 1]))
    loopBackTest(Call, ("aaa", [("type", 1)], []))
    loopBackTest(Call, ("aaa", [("type", "isolated")], [23]))
    loopBackTest(Call, ("aaa", [], \
                        [{"name" : "beaver", "value" : [987654321, 2, 3.0] }]))


def serializeReplyTest():    
    loopBackTestTyped( Reply, ([], True, 1) )
    loopBackTestTyped( Reply, ([], True, {"code" : [1, 2]}) )
    loopBackTestTyped( Reply, ([], False, {}) )
    loopBackTestTyped( Reply, ([], False, {"code" : "value"}) )


def referenceTest():
    m = {"name" : "beaver", "value" : [987654321, 2, 3.0] }
    loopBackTest(Call, ("aaa", [], [m, m]))
    a = [1, 2, 3]
    a[2] = a
    loopBackTest(Call, ("aaa", [], [a]))
    b = [a, 1]
    a[0] = b
    loopBackTest(Call, ("aaa", [], [b, a]))
    

def callTest():
    url = "http://localhost:8080/discore/party"
    try:
        proxy = HttpProxy(url)
        print proxy.getLocalMember()
        
        ##    Some speed measurements
        ##    start = time()    
        ##    for i in range(1000):
        ##        proxy.getLocalMember()
        ##    fin = time()
        ##    print "one call costs", (fin - start)/1000, "sec."        
        
    except Exception, e:
        if e.args == (10061, 'Connection refused'):
            print "Warning: Server '" + url +  "'is not available. Can not perform callTest"
        else:
            raise e   
    

if __name__=="__main__":
    loopbackTest()
    serializeCallTest()
    serializeReplyTest()
    referenceTest()
        
    callTest()

    print "Tests passed."
