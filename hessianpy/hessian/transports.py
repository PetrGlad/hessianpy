#
# Hessian protocol implementation
# This file contains pluggable transport mechanisms.
#
# Protocol specification can be found here:
# http://www.caucho.com/resin-3.0/protocols/hessian-1.0-spec.xtp
#
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

__version__ = "0.5.0"
__revision__ = "$Rev$"

AUTH_BASIC = "basic"

def getTransportForProtocol(protocol):
    """ returns the appropriate transport for a protocol identifier
    """
    return {
        "http": HTTPTransport, 
        "https": HTTPSTransport, 
    }[protocol]

class TransportError(Exception):
    """ Generic Exception for Transports
    """
    pass

class HessianTransport:
    """ Base class for all transports that can be used to talk to a Hessian.
    """

    def __init__(self, host = "", port = 0, path = ""):
        # initialization goes here
        self._host = host
        self._port = port
        self._path = path

    def authenticate(self, credentials):
        """ Invoke the authentication mechanism of the transport layer
	    if supported.
        """
        pass

    def request(self, outstream):
        """ Transport a request to the Hessian
        """
        pass

class HTTPTransport(HessianTransport):
    """ Transport the Hessian protocol via plain old unsecure HTTP
    """
    
    def __init__(self, host = "localhost", port = 0, path = "/", use_ssl = False):
        if port == 0:
            port = {
                True: httplib.HTTPS_PORT, 
                False: httplib.HTTP_PORT, 
            }[use_ssl]
        HessianTransport.__init__(self, host, port, path)
        self._connection = {
            True: httplib.HTTPSConnection, 
            False: httplib.HTTPConnection, 
        }[use_ssl](self._host, self._port)
        self._headers = {
            "Host" : self._host, 
            "User-Agent" : "HessianPy/%s" % __version__ }

    def authenticate(self, credentials):
        """ Authenticate to the server using BasicAuthentication.
        Actully just stores the values, since real authentication is performed 
        on every single request.

        @param credentials tuple consisting of username and password
        @returns True, since there is no way of telling, whether the credentials are correct
        """
        # store username and password for later use
        self._headers["Authorization"] = "Basic %s" % base64.encodestring(
             "%s:%s" % (credentials["username"], 
             credentials["password"])).rstrip()
        return True

    def request(self, outstream):
        """ Send the request via HTTP
	    """
        # pass it to the server
        self._connection.request("POST", self._path, outstream.getvalue(), 
            self._headers)
        response = self._connection.getresponse()
        if not response.status == httplib.OK:
            # tbd: analyze error code and take appropriate actions
            raise Exception("HTTP Error %d: %s" %
                (response.status, response.reason))
        result = StringIO(response.read())
        response.close()
        return result

class HTTPSTransport(HTTPTransport):
    """ Transport the Hessian protocol via SSL encrypted HTTP
    """

    def __init__(self, host = "localhost", port = 0, path = "/"):
        HTTPTransport.__init__(self, host, port, path, True)
