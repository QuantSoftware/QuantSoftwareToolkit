'''Author: Sourabh Bajaj'''
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name='QSTK',
    version='0.2.8',
    author='Sourabh Bajaj',
    packages=find_packages(),
    namespace_packages=['QSTK'],
    include_package_data=True,
    long_description=open('README.md').read(),
    author_email='sourabh@sourabhbajaj.com',
    url='https://github.com/tucker777/QuantSoftwareToolkit',
    license=open('LICENSE.txt').read(),
    description='QuantSoftware Toolkit',
    install_requires=[
        "numpy >= 1.6.1",
        "scipy >= 0.9.0",
        "matplotlib >= 1.1.0",
        "pandas >= 0.7.3",
        "python-dateutil == 1.5",
        "scikit-learn >= 0.11",
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
      ],
)
