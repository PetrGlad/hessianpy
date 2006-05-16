This directory contains hessian protocol implementation.
Author Petr Gladkikh (batyi at sourceforge net)

See http://www.caucho.com/resin-3.0/protocols/hessian.xtp for hessian 
protocol introduction. Protocol specification is at 
http://www.caucho.com/resin-3.0/protocols/hessian-1.0-spec.xtp
See hello.py for sample code.

Note that (optional) HTTPS test requires OpenSSL library (see http://openssl.org) 
and wrapper pyOpenSSL (see http://pyopenssl.sourceforge.net).
Note that HTTPS support in Python may not be enabled by default 
and you may need to add it separately (namely add library PYTHON_HOME/DLLs/_ssl.pyd).


	REQUIREMENTS
	
Python 2.4 or higher.


	INSTALLATION

Nothing special: just unpack this library into Python's lib directory or,
if you prefer, include directory with unpacked library into your PYTHON_PATH.


	RELEASE NOTES

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
