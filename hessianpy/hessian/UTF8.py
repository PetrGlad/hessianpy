# -*- coding: UTF-8 -*-
#
# This file contains UTF8 manipulation code.
# (It would be nice to use standard encoders, but they do not 
# allow reading symbol by symbol.)
#
# !!!NOTE!!! Only unicode symbols in 0..65536 are supported
#
# Unicode UTF-8
#  0x00000000 .. 0x0000007F: 0xxxxxxx
#  0x00000080 .. 0x000007FF: 110xxxxx 10xxxxxx
#  0x00000800 .. 0x0000FFFF: 1110xxxx 10xxxxxx 10xxxxxx
#  0x00010000 .. 0x001FFFFF: 11110xxx 10xxxxxx 10xxxxxx 10xxxxxx
#
# Copyright 2006 Petr Gladkikh (batyi at users sourceforge net)
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
__revision__ = "$Rev: 44 $"


# Masks that select code point bits in 1-st byte of UTF8 code point sequence
BYTE_MASKS = [0x7f, 0x1f, 0x0f, 0x07]

# Bounds of code point ranges that need different number of bytes in UTF8 sequence
BYTE_RANGES = [0x0000007F, 0x000007FF, 0x0000FFFF, 0x001FFFFF]

# bit-marks for first byte in UTF8 code point sequence that declare length of sequence
FIRST_MARKS = [0, 0xc0, 0xe0, 0xf0]


class UTF8Exception(Exception):
    pass


def readSymbolPy(sourceFun):
    first = sourceFun(1)
    if len(first) == 0:
        return None
    b = ord(first)    
    if (b & 0x80) == 0x00:
        return b # ASCII subset        

    mask = 0xf8
    pattern = 0xf0 
    byteLen = 4
    while byteLen > 1:         
        if (b & mask) == pattern:
            codePoint = 0xff & (b & ~mask)
            break
        byteLen -= 1
        mask = 0xff & (mask << 1)
        pattern = 0xff & (pattern << 1)
    else:  
        raise UTF8Exception("Incorrect UTF-8 encoding"
                         + " (first octet of symbol = 0x%x)" % b)    
    while byteLen > 1:
        ch = sourceFun(1)        
        if len(ch) == 0:
            raise UTF8Exception("Incorrect UTF-8 encoding"
                            + " (premature stream end)")        
        b = ord(ch)
        if (b & 0xc0) != 0x80:
            raise UTF8Exception("Incorrect UTF-8 encoding"
                        + " (trailing octet of symbol = 0x%x)" % b)
        codePoint <<= 6
        codePoint |= b & 0x3f
        byteLen -= 1        
    return codePoint


def symbolToUTF8Py(codePoint):    
    byteLen = 1
    for k in BYTE_RANGES:
        if codePoint <= k:
            break
        byteLen += 1
    else:
        raise UTF8Exception("Can not encode codePoint "
                        + codePoint + " in UTF-8. It is bigger than 0x001FFFFF")
                
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
        
    result[0] = chr(FIRST_MARKS[byteLen - 1] | c)
    return result

readSymbol = readSymbolPy
symbolToUTF8 = symbolToUTF8Py
 
def readString(source, size):
    return u"".join([unichr(readSymbol(source.read)) for _ in range(size)])
