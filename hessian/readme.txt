This directory contains hessian protocol implementation.
Author Petr Gladkikh (batyi at mail ru)

See http://www.caucho.com/resin-3.0/protocols/hessian.xtp for hessian protocol introduction.
Protocol specification http://www.caucho.com/resin-3.0/protocols/hessian-1.0-spec.xtp
See hello.py for sample code.


	RELEASE NOTES

v0.2 2005-11-21
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
memstream.py - auxiliary stream implementation
test.py - tests for this library


	WHY

I wrote this implementation because pythonic implementation that is
published at the caucho.com site (see http://www.caucho.com/hessian/) does
not work and seems to be abandoned.
