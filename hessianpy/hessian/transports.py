#
# Hessian protocol implementation
# This file contains pluggable transport mechanisms.
#
# Protocol specification can be found here:
# http://www.caucho.com/resin-3.0/protocols/hessian-1.0-spec.xtp
#
# Copyright 2006 Bernd Stolle (thebee at sourceforge net)
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
"""
Transports for Hessian.

Content:
* HessianTransport - abstract base class
* HTTPTransport - talk hessian over simple unencrypted HTTP,
    support for BasicAuthentication
"""

import base64
import httplib
from StringIO import StringIO
import urllib2

__revision__ = "$Rev$"
__version__ = "0.5.2"


AUTH_BASIC = "basic"


def getTransportForProtocol(protocol):
    """ Returns the appropriate transport for a protocol's URL scheme
    """
    return {
        "http": BasicUrlLibTransport, 
        "https": BasicUrlLibTransport, 
    } [protocol]

class TransportError(Exception):
    """ Generic Exception for Transports
    """
    pass

class HessianTransport:
    """ Base class for all transports that can be used to talk 
    to a Hessian server. 
    """

    def __init__(self, uri, credentials):
        self._uri = uri
        self._credentials = credentials

    def request(self, outstream):
        " Send stream to server "
        raise Exception("Method is not implemented")
    
    
class BasicUrlLibTransport(HessianTransport):
    """ Transport handler that uses urllib2. 
    Basic authentication scheme is used. """
    
    def __init__(self, uri, credentials):
        HessianTransport.__init__(self, uri, credentials)
        print "init:uri:", uri, "; cred:", self._credentials # debug
        
        if (False and self._credentials != None):
            # HTTPPasswordMgrWithDefaultRealm()            
            auth_handler = urllib2.HTTPBasicAuthHandler()
            auth_handler.parent
            # HTTPDigestAuthHandler                
            auth_handler.add_password(None, None, 
                                      self._credentials['username'], 
                                      self._credentials['password'])
            self._opener = urllib2.build_opener(auth_handler)
        else:
            self._opener = urllib2.build_opener()
            
        self._opener.addheaders = [
                     ('User-agent', 'HessianPy/%s' % __version__)
                     ]
#        # store username and password for later use
#        self.opener.addheaders["Authorization"] = "Basic %s" % base64.encodestring(
#             "%s:%s" % (credentials["username"], 
#             credentials["password"])).rstrip() 
    
  
    def request(self, outstream):
        r = urllib2.Request(self._uri, outstream.read())
        response = self._opener.open(r)     
        result = StringIO(response.read())
        response.close()
        return result        
  
