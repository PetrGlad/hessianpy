# -*- coding: UTF-8 -*-
#
# This file contains UTF8 manipulation code.
# (It would be nice to use standard encoders, but they do not 
# allow to read symbol by symbol.)
#
# Unicode UTF-8
#  0x00000000 — 0x0000007F: 0xxxxxxx
#  0x00000080 — 0x000007FF: 110xxxxx 10xxxxxx
#  0x00000800 — 0x0000FFFF: 1110xxxx 10xxxxxx 10xxxxxx
#  0x00010000 — 0x001FFFFF: 11110xxx 10xxxxxx 10xxxxxx 10xxxxxx
#
# Copyright 2006 Petr Gladkikh (batyi at sourceforge net)
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

def readSymbol(sourceFun):
    first = sourceFun(1)
    if len(first) == 0:
        return None
    b = ord(first)
    # number of 1's: 0, 2, 3, 4
    byteLen = 1
    while b & 0x80:
        byteLen += 1        
        b <<= 1
    if byteLen > 4:
            raise Exception("UTF-8 Error: Incorrect UTF-8 encoding"
                            +" (first octet of symbol = 0x%x)" % ord(first))        
    elif byteLen > 1:
            byteLen -= 1            
    mask = [0x7f, 0x1f, 0x0f, 0x07] [byteLen - 1]
    codePoint = ord(first) & mask
    for k in range(1, byteLen):
        ch = sourceFun(1)
        if len(ch) == 0:
            raise Exception("UTF-8 Error: Incorrect UTF-8 encoding"
                            +" (premature stream end)")
        codePoint <<= 6        
        codePoint |= ord(ch) & 0x3f
        
    return codePoint


def symbolToUTF8(codePoint):    
    byteLen = 1
    for k in [0x0000007F, 0x000007FF, 0x0000FFFF, 0x001FFFFF]:
        if codePoint <= k:
            break
        byteLen += 1
    else:
        raise Exception("UTF-8 Error: Can not encode codePoint ["
                        + codePoint + "] in UTF-8. It is bigger than 0x001FFFFF")
                
    result = [0] * byteLen  
    
    c = codePoint    
    k = byteLen - 1
    if byteLen > 3:
        result[k] = chr(c & 0x3f | 0x80)
        c >>= 6        
        k -= 1
    if byteLen > 2:
        result[k] = chr(c & 0x3f | 0x80)
        c >>= 6
        k -= 1
    if byteLen > 1:
        result[k] = chr(c & 0x3f | 0x80)
        c >>= 6
        k -= 1
        
    firstMark = [0, 0xc0, 0xe0, 0xf0] [byteLen - 1]
    result[0] = chr(firstMark | c)
    
    # print "thisByte = %x; mark = %x; firstMark = %x" % ((mark | codePoint & 0x7f), mark, firstMark)
    # print "firstMark = %x" % firstMark
    # print result
    
    return result
        

def test():
    # TODO Test exceptions    
    from StringIO import StringIO
    src = u"""
    В этом нет ничего нового,
    Ибо вообще ничего нового нет.
        Николай Рерих        
    ÀùúûüýþÿĀāĂăĄąĆćĈĉ
    $¢£¤¥₣₤₧₪₫€
    """    
    u0 = src.encode("UTF-8")
    u1 = ""
    for c in src:
        u1 += "".join(symbolToUTF8(ord(c)))
    assert u1.decode("UTF-8") == src
    s = []
    k = 0
    s_read = StringIO(u1)
    while True:
        repr = readSymbol(s_read.read)
        if repr == None:
            break
        s.append(unichr(repr))
        
    s = u"".join(s)
    assert s == src


if __name__ == "__main__":
        test()
        print "Tests passed."
