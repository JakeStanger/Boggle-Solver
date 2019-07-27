from setuptools import setup

setup(
    name='Boggle-Solver',
    version='1.0.0',
    packages=['boggle-solver'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask>=1'],
    url='https://github.com/JakeStanger/Boggle-Solver',
    license='MIT',
    author='Jake Stanger',
    author_email='mail@jstanger.dev',
    description='Flask app to find words on a given Boggle board.'
)
