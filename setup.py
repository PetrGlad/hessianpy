import hessian
from distutils.core import setup

setup(name='HessianPy',
	version=hessian.__version__,
	description="Implementation of Hessian RPC protocol",
	author="Petr Gladkikh",
	author_email="batyi@users.sourceforge.net",
	url="http://hessianpy.sourceforge.net",
	license="Apache License 2.0",
	platforms="Platform independent",	
	long_description="""HessianPy is an implementation of Hessian protocol. Hessian is platform
independent binary RPC (remote procedure call) protocol (see 
http://hessian.caucho.com/doc/hessian-1.0-spec.xtp for more detailed description).""",
	
        packages=['hessian', 'hessian.test'],
        package_data={'hessian.test': ['server.pem']},
    )
