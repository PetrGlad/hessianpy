from distutils.core import setup
setup(name='HessianPy',
	version='0.5.5',
	description="Implementation of Hessian RPC protocol",
	author="Petr Gladkikh",
	author_email="batyi@users.sourceforge.net",
	url="http://hessianpy.sourceforge.net",
	license="Apache License 2.0",
	platforms="Pure Python",
	packages=['hessian', 'hessian.test'],
	long_description="See http://www.caucho.com/resin-3.0/protocols/hessian.xtp for introduction into Hessian RPC protocol.",

	package_data={'hessian': ['*.txt', '*.pem']}

    )

#package_dir = {'hessian': 'Lib'}

#	data_files=[('', ['licence.txt', 'readme.txt', 'runtest', 'server.pem', 'TODO.txt'])]