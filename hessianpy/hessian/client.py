#
# Hessian protocol implementation
# This file contains client proxy code.
#
# Protocol specification can be found here:
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
import urllib
import httplib
from StringIO import StringIO
import hessian


__version__ = "0.3.4"


class Method:
    "Encapsulates the method to be called"
    def __init__(self, invoker, method):
        self.invoker = invoker
        self.method = method

    def __call__(self, *args):
        return self.invoker(self.method, args)


class HttpProxy:
    """ A Hessian proxy class.
     TODO: support HTTPS (and perhaps other transports - why not ssh?).
    """
    
    def __init__(self, url):
        self.url = url
        transport, uri = urllib.splittype(url)    
        if transport != "http":
            raise IOError("Unsupported transport protocol '" + transport + "'")
        self.host, self.uri = urllib.splithost(uri)
    
    def __invoke(self, method, params):
        s = StringIO()
        hessian.writeObject(hessian.WriteContext(s), \
                            (method, [], params), \
                            hessian.Call())
        request = s.getvalue()
        h = httplib.HTTPConnection(self.host)
        h.request("POST", \
                    self.uri, \
                    s.getvalue(), \
                    {"Host" : self.host, \
                    "User-Agent" : "HessianPy/%s" % __version__})

        response = h.getresponse()
        
        if response.status != httplib.OK:
            raise Exception("HTTP Error %d: %s" % (response.status, response.reason))

        inStream = StringIO(response.read())
        # print "\nGot buffer:[" + inStream.buf + "]" # debug
        ctx = hessian.ParseContext(inStream)
        (headers, status, value) = hessian.Reply().read(ctx, ctx.read(1))        
        # print "Call result:", headers, status, value # debug
        if not status:
            # value is a Hessian error description
            raise Exception(value) 
        return value

    def __getattr__(self, name):
        # encapsulate the method call
        return Method(self.__invoke, name)
    
    def deref(object):
        "Walk recursively and replace hessian.RemoteReference with live proxies"
        assert False # todo
        pass
    
    def drain(object):
        "Walk recursively and replace HessiaReferences with hessian.RemoteReference"
        assert False # todo
        pass