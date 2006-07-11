# -*- coding: UTF-8 -*-
#
# Hessian protocol implementation
# This file contains client proxy code.
#
# Protocol specification can be found here:
# http://www.caucho.com/resin-3.0/protocols/hessian-1.0-spec.xtp
#
# Copyright 2005, 2006 Petr Gladkikh (batyi at sourceforge net)
# Copyright 2006 Bernd Stolle (thebee at sourceforge net)
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
import hessian
import transports
import urlparse
from StringIO import StringIO


__revision__ = "$Rev$"


class Method:
    "Encapsulates the method to be called"
    def __init__(self, invoker, method):
        self.invoker = invoker
        self.method = method

    def __call__(self, *args):
        return self.invoker(self.method, args)

class HessianProxy:
    """ A Hessian Proxy Class.
    Supported transport mechanisms are pluggable and are defined in transports.py
    """

    typename = "client.HessianProxy"
    
    def __init__(self, url, authdata = {                       
                        "username": "", 
                        "password": "" }):
        self.url = url
        url_tuple  = urlparse.urlparse(url)
        protocol = url_tuple[0]
        #host_with_port = url_tuple[1]
        #path = "%s?%s" % (url_tuple[2], url_tuple[4])
        #host, port = split_host_and_port(host_with_port)        
        
        self._authdata = authdata
        transport_class = transports.getTransportForProtocol(protocol)
        self._transport = transport_class(url, authdata)
        
    def __invoke(self, method, params):        
        request = StringIO()        
        hessian.writeObject(
                            hessian.WriteContext(request, self.drain), 
                            (method, [], params), 
                            hessian.Call())
        
        # print "request.value (" + `len(request.getvalue())` + ") =", `request.getvalue()` # debug        
        request.seek(0)
        response = self._transport.request(request)

        # this will retain same credential for all interfaces we are working with
        deref_f = lambda x : self.deref(x, self._authdata)
        
        ctx = hessian.ParseContext(response, deref_f)
        (headers, status, value) = hessian.Reply().read(ctx, ctx.read(1))
        if not status:
            # value is a Hessian error description
            raise Exception(value) 
        else:
            return value
            
    def __getattr__(self, name):
        if name[:2] == "__" and name[-2:] == "__":
            # exclude special methods from remote invocation as it 
            # causes more trouble than helps
            
            # print "attribute", name, "ignored" # debug
            return None
        else:
            return Method(self.__invoke, name)

    @staticmethod
    def deref(obj, auth):
        "Replace hessian.RemoteReference with live proxy"
        if hasattr(obj, "typename") and obj.typename == "hessian.RemoteReference":
           return HessianProxy(obj.url, auth)
        else:
           return obj
                                                       
    @staticmethod
    def drain(obj):
        "Replace Hessian proxy with hessian.RemoteReference"
        if hasattr(obj, "typename") and obj.typename == "client.HessianProxy":
            return hessian.RemoteReference(obj.url)
        else:
            return obj
