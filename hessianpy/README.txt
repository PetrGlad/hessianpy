This directory contains hessian protocol implementation.
Author Petr Gladkikh (batyi at users.sourceforge.net)

See http://hessian.caucho.com/ for Hessian protocol introduction.
Protocol specification is at 
http://hessian.caucho.com/doc/hessian-1.0-spec.xtp
See hello.py file for sample code.

If you need to send Hessian's Xml, then construct hessian.hessian.XmlString
and pass it as a remote call parameter.

Sequence types are mapped as follows:
    Python -> Hessian -> Python
    tuple     array      list
    list      array      list     
    str       binary     str
    unicode   string     unicode    
    datetime  date       datetime


	REQUIREMENTS
	
Python 2.6 
You can download Python interpreter from http://python.org/.

Note that (optional) HTTPS test requires OpenSSL library (see http://openssl.org) 
and wrapper pyOpenSSL (see http://pyopenssl.sourceforge.net).
Note that HTTPS support in Python may not be enabled by default 
and you may need to add it separately (namely add library PYTHON_HOME/DLLs/_ssl.pyd).


	INSTALLATION

Standard Python module installation procedure (distutils) is used. 
Typical installation procedure is:
1. Unpack archive 
2. Change current directory to root of unpacked files
3. Execute: python setup.py install

For more details see "Installing Python Modules" section in Python's documentation. 


	RELEASE NOTES

v1.0.3 2009-10-23
    1. Python 2.6 is now required ("except Exception as var" construction is used)
    2. Added support for Date type   
        (see patch https://sourceforge.net/tracker/?func=detail&aid=2881772&group_id=154438&atid=791785 at sourceforge.net)
    3. Remote exceptions handling changed (exception object attributes 
        and .args are retained).
    4. Sample server shutdown cleaned up

v1.0.2 2008-07-10
	1. Corrected vector length check during serialization 
	(bug #2014787, reported by Jeon Chanseok).

v1.0.1 2008-01-01
	1. Changed binary data serialization. Python's "str" type is now mapped
	to Hessian's "binary". 
	2. Stricter and slightly faster UTF-8 parser.
	3. Tests improved.
	4. Happy new year!

v1.0.0 2007-08-11
	1. Corrected serialization of failure result.
	2. Client can now specify Hessian's XML and binary types.
	3. Corrected reply serialization (headers are now read correctly, 
	thanks to Mark Santos for pointing to this bug).
	4. Content-Length HTTP header is now sent with request
	
v0.5.6 2007-05-13
	1. Improved performance of UTF8 encoder/decoder. It is now 10-50% faster. 
	2. CPython 2.5 is now recommended (although 2.4 is still supported).
	
v0.5.5 2006-12-17
	1. Added standard module installation script. Files rearranged in more standard way. 
	2. Code cleanups. In particular __class__ attribute is now used in serializer
	code instead of explicit typename attribute.
	
v0.5.4 2006-08-21
	1. Corrected bug with http headers in remote request that prevented HessianPy 
	from working with servlet-based implementation of Hessian.
	
	The reason of this bug turned out to be less esoteric then I thought.
	Data encoding was not specified for request and was automaticaly set 
	by urllib2.Request to application/x-www-form-urlencoded.
	Servlet then dutifully tried to parse request data as HTTP form post.
	Explicitly setting content type to application/octet-stream solved 
	the problem.

v0.5.3 2006-05-02
	1. Transports refactored to use urllib2. Initial implementation assumed
	that HTTPConnection allows keeping connections open thus enhancing 
	performance. This is wrong. urllib2 provides more functionality 
	and is simpler to use so code is now shorter and cleaner.
	2. Small code cleanups: Imports are now "normalized".
	3. NOTE: Tests with public Caucho's interface was not passed. 
	There's some "internal server error". Although this release of 
	HessianPy works well with my own Hessian-3.0.13+Jetty+Spring_remoting.

v0.5.1 2006-05-18
	1. Incompatibility with Java implementation fixed. 
	Specification of the protocol does not specify in what units length of UTF-8 
	data is measured. Initial HessianPy implementation counted all lenghts in 
	octets whereas Java implementation in Unicode symbols.
	Now HessianPy writes string and XML data lenghts in symbols too. Now all
	tests with non-ascii Unicode symbols pass. This however slowed down 
	serialization as we need to write characters one by one.	

v0.5 2006-04-09
	1. Integrated support for HTTP authorization and HTTPS (Contributed by Bernd Stolle)
	2. Added simple HTTPS test server. This server requires OpenSSL wrapper pyOpenSSL 
	(see http://pyopenssl.sourceforge.net). Note: if you need this wrapper under Windows 
	you may need to tweak wrapper's source a little (see 'patches' section in pyOpenSSL 
	project's page at sourceforge.net)

v0.4 2006-02-25
	First "beta" version. I think, tests now cover all significant parts of protocol.
	1. References to remote interfaces now supported
	2. Support for splitted sequences tested
	3. Minor code cleanups
	
v0.3.3 2006-02-18
	1. Remote exception handling fixed, self-hosted remote call tests added	
	2. Simple RPC server added. This server is intended for testing purposes.
	3. Note: TODO has changed

v0.3.2 2006-01-21
	1. Tuple serialization added (it is serialized as an array)
	2. Now test suite pulls every method in 
"http://www.caucho.com/hessian/test/basic" public interface. 
	2.1 Although one apparent exception handling bug fixed, can not
verify it because call to BasicAPI.fault() hangs (can not get
response from server).
	
v0.3.1 2005-12-11
	1. Added support for XML objects (as plain strings) 
	2. Added partial (no serialization) implementation of remote interface reference.
	3. Got rid of memstream.py - now standard StringIO is used.
Note that only plain HTTP is supported as a transport. The library still lacks 
server-side functionality which is necessary to test all patrs of the library.

v0.3 2005-11-21
Initial implementation. It does not support remote references. Look for
"TODO" string in source to find not implemented parts. It also may have
problems with Unicode strings (it's not tested yet). The code also needs to
be streamlined a little. 
Note that this implementation contains only client code. Server-side
implementation would require some kind of HTTP server.


	FILES

client.py - client proxy code
licence.txt - contains distribtution license.
hello.py - contains sample client code.
hessian.py - serializing/deserializing code
runtest - command line that runs test
server.py - simple HTTP RPC server (used in testing)
secureServer.py - simple HTTPS RPC server (used in testing)
server.pem - sample OpenSSL keypair (used in testing)
test/test.py - tests for this library
testSecure/test.py - HTTPS tests for this library
transports.py - transport protocols
UTF8.py - UTF-8 encoder/decoder


	WHY

I wrote this implementation because pythonic implementation that is
published at the caucho.com site (see http://www.caucho.com/hessian/) does
not work and seems to be abandoned. On the other hand the protocol is rather
straightforward and can be implemented with reasonable effort.
