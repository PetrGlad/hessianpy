#
# Hessian protocol implementation
# This file contains serialization/deserialization code.
# Note: Please look for "TODO" string to find not implemented parts.
#
# Protocol specification can be found here
# http://www.caucho.com/resin-3.0/protocols/hessian-1.0-spec.xtp
#
# Copyright 2005, 2006 Petr Gladkikh (batyi at sourceforge net)
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
from struct import pack, unpack


types = []
CODE_MAP = {}
TYPE_MAP = {}


class HessianError(Exception):
    "This exception indicates a runtime error in 'hessian' module"
    pass


# describes contract for value serializers
class ValueStreamer:
    codes = None  # type code list
    ptype = None # Python type of value
    
    def read(self, stream):
        "Init value from Stream"
        assert False # abstract        
    
    def write(self, stream, value):
        "Write value from Stream"
        assert False # abstract


def readObject(stream):
    prefix = stream.read(1)
    return readObjectByPrefix(stream, prefix)


def readObjectByPrefix(stream, prefix):
    return CODE_MAP[prefix].read(stream, prefix)


def writeObject(stream, value, htype):
    "Write value with specified type"
    if htype is None: # autodetect type
        htype = TYPE_MAP[type(value)]
    htype.write(stream, value)       


def readShort(stream):
    return unpack('>H', stream.read(2))[0]


def writeShort(stream, value):
    stream.write(pack(">H", value))


def readVersion(stream):
    (major, minor) = unpack("BB", stream.read(2))
    if  (major, minor) != (1, 0):
        raise HessianError("Unsupported protocol version " + `major` + "." + `minor`)
    

def writeVersion(stream):
    stream.write("\x01\x00")

    
class SimpleValue:
    "Single valued types (none)"
    def read(self, stream, prefix):
        assert prefix in self.codes
        return self.value
    
    def write(self, stream, value):
        assert value == self.value
        stream.write(self.codes[0])


class Null(SimpleValue):
    codes = ["N"]
    ptype = type(None)
    value = None
types.append(Null)

    
class Bool:
    codes = ["F", "T"]
    ptype = bool
    
    def read(self, stream, prefix):
        assert prefix in self.codes
        return prefix == self.codes[1]
    
    def write(self, stream, value):
        assert type(value) == bool
        k = 0
        if value: k = 1
        stream.write(self.codes[k])
types.append(Bool)


class BasicInt:
    codes = []
    
    def read(self, stream, prefix):
        assert prefix in self.codes
        dat = stream.read(4)
        assert len(dat) == 4
        return unpack(">l", dat)[0]
    
    def write(self, stream, value):
        stream.write(self.codes[0])
        stream.write(pack(">l", value))

   
class Int(BasicInt):
    codes = ["I"]
    ptype = int
types.append(Int)


class Long:
    codes = ["L"]
    ptype = long
    
    def read(self, stream, prefix):
        assert prefix in self.codes
        return unpack('>q', stream.read(8))[0]
    
    def write(self, stream, value):
        stream.write(self.codes[0])
        stream.write(pack(">q", value))
types.append(Long)


class Double:
    codes = ["D"]
    ptype = float

    def read(self, stream, prefix):
        assert prefix in self.codes
        return unpack('>d', stream.read(8))[0]
        
    def write(self, stream, value):
        stream.write(self.codes[0])
        stream.write(pack(">d", value))
types.append(Double)


class ShortSequence:
    codes = []

    def read(self, stream, prefix):
        count = readShort(stream)
        return stream.read(count)

    def write(self, stream, value):
        "We could split large data into chunks here."
        stream.write(self.codes[0])
        writeShort(stream, len(value))
        stream.write(value)    


class Chunked(ShortSequence):
    """'codes' mean following: codes[1] starts all chunks but last;
    codes[0] starts last chunk."""

    readChunk = ShortSequence.read # shortcut

    def read(self, stream, prefix):
        result = "";
        while (prefix == self.codes[1]):
            result += self.readChunk(stream)
            prefix = stream.read(1)
        assert prefix == self.codes[0]
        result += self.readChunk(stream, prefix)
        return result

    # to write in chunks need to overload "write" method

    
class String(Chunked):
    codes = ["S", "s"]
    ptype = str
types.append(String)


class Binary(Chunked):
    codes = ["B", "b"]
types.append(Binary)


class TypeName(ShortSequence):
    codes = ["t"]    
types.append(TypeName)


class Length(BasicInt):
    codes = ["l"]
types.append(Length)


def writeReferenced(stream, writeMethod, obj):
    """Write reference if object has been met before.
    Else write object itself."""
    
    objId = stream.getRefId(obj)
    if objId != -1:
        Ref().write(stream, objId)
    else:
        writeMethod(stream, obj)
        

class Array:
    codes = ["V"]
    ptype = list

    type_streamer = TypeName()
    length_streamer = Length()
    
    def read(self, stream, prefix):
        assert prefix == "V"
        prefix = stream.read(1)
        if prefix in self.type_streamer.codes:
            self.type_streamer.read(stream, prefix)
            prefix = stream.read(1)
        count = self.length_streamer.read(stream, prefix)        
        prefix = stream.read(1)        
        result = []
        stream.referencedObjects.append(result)        
        while prefix != "z":        
            result.append(readObjectByPrefix(stream, prefix))
            prefix = stream.read(1)
        assert count == len(result)
        assert prefix == "z"
        return result

    def _write(self, stream, value):
        stream.write(self.codes[0])
        
        # we'll not write type marker because we may only guess it
        # self.type_streamer.write(stream, "something")
        
        self.length_streamer.write(stream, len(value))
        for o in value:
            writeObject(stream, o, None)
        stream.write("z")
        
    def write(self, stream, value):
        writeReferenced(stream, self._write, value)
types.append(Array)


class Tuple(Array):
    "This class serialises tuples. They are always read as arrays"
    codes = ["V"]
    ptype = tuple
types.append(Tuple)    


class Map:
    codes = ["M"]
    ptype = dict

    type_streamer = TypeName()
    
    def read(self, stream, prefix):
        assert prefix in self.codes
        prefix = stream.read(1)
        if prefix in TypeName.codes:
            self.type_streamer.read(stream, prefix)
            prefix = stream.read(1)
        result = {}
        stream.referencedObjects.append(result)        
        while prefix != "z":
            key = readObjectByPrefix(stream, prefix)            
            value = readObject(stream)
            result[key] = value
            prefix = stream.read(1)
        return result
    
    def _write(self, stream, mapping):
        stream.write(self.codes[0])
        for k, v in mapping.items():
            writeObject(stream, k, None)
            writeObject(stream, v, None)
        stream.write("z")

    def write(self, stream, value):
        writeReferenced(stream, self._write, value)
types.append(Map)    


class Ref(BasicInt):
    """ Reference to a previously occured object 
    (allows sharing objects in a map or a list) """
    codes = ["R"]

    def read(self, stream, prefix):
        refId = BasicInt.read(self, stream, prefix)
        return stream.referencedObjects[refId]

    def write(self, stream, objId):
        BasicInt.write(self, stream, objId)
types.append(Ref)


class Header:
    "A (name, value) pair"
    codes = ["H"]

    title_streamer = ShortSequence()
    title_streamer.codes = codes
    
    def read(self, stream, prefix):
        assert prefix in self.codes
        # read header title
        title = self.title_streamer.read(stream, prefix)
        assert len(title) > 0
        # read header value
        value = readObject(stream)        
        return (title, value)
    
    def write(self, stream, header):
        title, value = header
        # write title
        self.title_streamer.write(stream, title)
        # write value
        writeObject(stream, value, None)
types.append(Header)


class Method(ShortSequence):
    codes = ["m"]
types.append(Method)


class Xml(Chunked):
    codes = ["X", "x"]
types.append(Xml)


class Call:
    "Represents request to a remote interface."
    codes = ["c"]
    
    method_streamer = Method()
    header_streamer = Header()
    
    def read(self, stream, prefix):
        assert prefix == self.codes[0]
        readVersion(stream)
        prefix = stream.read(1)
        
        # read headers
        headers = []
        while prefix == self.header_streamer.codes[0]:
            headers.append(self.header_streamer.read(stream, prefix))
            prefix = stream.read(1)
            
        # read method
        method = self.method_streamer.read(stream, prefix)
        prefix = stream.read(1)
        
        # read params
        params = []        
        while prefix != "z":
            params.append(readObjectByPrefix(stream, prefix))
            prefix = stream.read(1)
            
        return (method, headers, params)

    def write(self, stream, value):
        # headers can be None or map of headers (header title->value)
        method, headers, params = value
        stream.write(self.codes[0])
        writeVersion(stream)
        
        # write headers
        if headers != None:
            for h in headers:
                self.header_streamer.write(stream, h)
                
        # write method
        self.method_streamer.write(stream, method)
        
        # write params
        if params != None:
            for v in params:
                writeObject(stream, v, None)
                
        stream.write("z");
types.append(Call)


class Fault:
    "Remote_call error_description."
    codes = ["f"]
    
    def read(self, stream, prefix):
        assert prefix in self.codes
        result = {}
        prefix = stream.read(1)
        while prefix != "z":
            k = readObjectByPrefix(stream, prefix)
            prefix = stream.read(1)
            v = readObjectByPrefix(stream, prefix)
            prefix = stream.read(1)
            result[k] = v
        return result
    
    def write(self, stream, fault):
        stream.write(self.codes[0])
        for k, v in fault.items():
            writeObject(stream, k, None)
            writeObject(stream, v, None)            
types.append(Fault)


class Reply:
    "Result of remote call."
    
    """Note "Remote" code clashes with "Reply" code 
    and Reply is always read explicitly. 
    Thus do not register it in global type map. """
    autoRegister = False
    
    codes = ["r"]

    header_streamer = Header()
    fault_streamer = Fault()
    
    def read(self, stream, prefix):
        assert prefix in self.codes[0]
        # parse header 'r' x01 x00 ... 'z'

        readVersion(stream)        
        prefix = stream.read(1)
        # parse headers
        headers = []
        while prefix in self.header_streamer.codes:
            headers.append(self.header_streamer.read())
            prefix = stream.read(1)           

        succseeded = not prefix in self.fault_streamer.codes
        
        if succseeded:
            result = readObjectByPrefix(stream, prefix)
            prefix = stream.read(1)
            if prefix != 'z':
                raise "No closing marker in reply"
        else:
            result = self.fault_streamer.read(stream, prefix)
            # closing "z" is already read by Fault.read
        
        return (headers, succseeded, result)

    def write(self, stream, reply):
        (headers, succeeded, result) = reply
        stream.write(self.codes[0])
        writeVersion(stream)
        for h in headers:
            self.header_streamer.write(stream, h)
        if succeeded:
            writeObject(stream, result, None)
        else:
            self.fault_streamer.write(stream, result)
        stream.write("z")
types.append(Reply)


# We need it for class Remote. Unfortunately this introduces cyclic references
import client 

class Remote:
    "Reference to a remote interface."
    codes = ["r"]
    
    typename_streamer = TypeName()
    url_streamer = String()
        
    def read(self, stream, prefix):        
        assert prefix in self.codes
        # skip typeNmae of remote interface        
        self.typename_streamer.read(stream, stream.read(1))
        # read url
        url = self.url_streamer(stream, stream.read(1))
        
        # NOTE: non HTTP transports are not yet supported.
        # TODO: (See comments to HttpProxy class)
        return client.HttpProxy(url)
    
    def write(self, stream, remote):
        # TODO: decide what to accept here. 
        # Should we require proxy object here for sake of consitency? (see 'read' method)
        assert False # code is not tested.
        stream.write(self.codes[0])
        typeName, url = remote        
        self.type_streamer.write(stream, typeName)
        self.url_streamer.write(stream, url)
types.append(Remote)


def makeTypeMaps(types):
    """ Build maps that allow to find apropriate 
    serializer (by object type) or deserializer (by prefix symbol).
    """
    codeMap = {} # type code to streamer map
    typeMap = {} # python type to streamer map
    for c in types:
        streamer = c()
        
        if hasattr(streamer, "autoRegister") and not streamer.autoRegister:
            continue
        
        for ch in streamer.codes:
            # assert not ch in codeMap
            codeMap[ch] = streamer
        if hasattr(streamer, "ptype"):
            assert not streamer.ptype in typeMap
            typeMap[streamer.ptype] = streamer
    return codeMap, typeMap


CODE_MAP, TYPE_MAP = makeTypeMaps(types)


class ParseContext:    
    def __init__(self, stream):
        self.referencedObjects = [] # objects that may be referenced by Ref
        self.objectIds = {}
        self.stream = stream        
        self.read = stream.read


class WriteContext:
    def __init__(self, stream):
        self.objectIds = {} # is used for back references
        self.count = 0
        self.stream = stream
        self.write = stream.write
        
    def getRefId(self, obj):
        "Return numeric ref id if object has been already met"
        try:
            return self.objectIds[id(obj)]
        except KeyError, e:
            self.objectIds[id(obj)] = self.count
            self.count += 1
            return -1

            
if __name__ == "__main__":
    print "Registered types:"
    for t in types:
        print t, 
        for c in t.codes:
            print c, 
        print
