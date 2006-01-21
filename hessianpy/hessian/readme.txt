This directory contains hessian protocol implementation.
Author Petr Gladkikh (batyi at sourceforge net)

See http://www.caucho.com/resin-3.0/protocols/hessian.xtp for hessian 
protocol introduction. Protocol specification is at 
http://www.caucho.com/resin-3.0/protocols/hessian-1.0-spec.xtp
See hello.py for sample code.


	RELEASE NOTES

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

licence.txt - contains distribtution license.
hello.py - contains sample client code.
client.py - client proxy code
hessian.py - serialising/deserializing code
test.py - tests for this library


	WHY

I wrote this implementation because pythonic implementation that is
published at the caucho.com site (see http://www.caucho.com/hessian/) does
not work and seems to be abandoned. On the other hand the protocol is rather
straightforward and can be implemented with reasonable effort.
