from distutils.core import setup

setup(name='HessianPy',
	version='0.6',
	description="Implementation of Hessian RPC protocol",
	author="Petr Gladkikh",
	author_email="batyi@users.sourceforge.net",
	url="http://hessianpy.sourceforge.net",
	license="Apache License 2.0",
	platforms="Platform independent",	
	long_description="""Hessian is platform independent binary RPC (remote procedure call) protocol.
See http://www.caucho.com/resin-3.0/protocols/hessian.xtp for more detailed description.""",
	
	packages=['hessian', 'hessian.test'],
    package_data={'hessian.test': ['server.pem']},
    )
