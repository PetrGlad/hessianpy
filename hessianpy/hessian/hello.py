#
# Simplest hessian client example
#

import client

proxy = client.HttpProxy("http://www.caucho.com/hessian/test/basic")
print proxy.hello()
