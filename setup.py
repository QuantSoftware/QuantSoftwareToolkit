from distutils.core import setup

setup(
    name='QSTK',
    version='0.2.1',
    author='Sourabh Bajaj',
    packages=['QSTK', 'QSTK.qstkfeat', 'QSTK.qstklearn', 'QSTK.qstksim',
			  'QSTK.qstkstrat', 'QSTK.qstkstudy', 'QSTK.qstkutil', 'QSTK.qstktest'],
    long_description=open('README.md').read(),
    author_email='sourabhbajaj90@gmail.com',
    url='http://wiki.quantsoftware.org',
    license='LICENSE.txt',
    description='QuantSoftware Toolkit',
    install_requires=[
        "numpy >= 1.6.1",
        "scipy >= 0.10.0",
        "matplotlib >= 1.1.0",
        "pandas==0.7.3",
        "dateutil >= 1.5",
        "cvxopt >= 1.1.4",
        "scikit-learn >= 0.11",
    ],
)
