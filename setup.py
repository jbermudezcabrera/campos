from setuptools import setup, find_packages

__author__ = 'Juan Manuel Bermúdez Cabrera'

description = 'Helps you to quickly create and generate fully functional forms'

setup(
    name='campos',
    version='1.0.1',
    packages=find_packages(),

    url='https://github.com/jbermudezcabrera/campos',
    download_url='http://pypi.python.org/pypi/campos',
    license='MIT',

    description=description,
    long_description=open('README.rst').read(),

    author=__author__,
    author_email='jbermudezcabrera@gmail.com',

    install_requires=['qtpy'],
    platforms='OS Independent',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5']
)
