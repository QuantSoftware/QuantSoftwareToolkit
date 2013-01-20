# from distutils.core import setup
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
# import os

# def gen_data_files(*dirs):
#     results = []
#     for src_dir in dirs:
#         for root,dirs,files in os.walk(src_dir):
#             results.append((root, map(lambda f:root + "/" + f, files)))
#     return results

setup(
    name='QSTK',
    version='0.2.4',
    author='Sourabh Bajaj',
    # packages=['QSTK', 'QSTK/qstkfeat', 'QSTK/qstklearn', 'QSTK/qstksim',
    #           'QSTK.qstkstrat', 'QSTK.qstkstudy', 'QSTK/qstkutil',
    #           'QSTK.qstktools', 'QSTK.qstktest'],
    # package_dir={'': ''},
    # packages_data={'QSTK': ['QSData/Yahoo/*',
    #                         'QSData/Yahoo/Lists/*.txt'],
    #                'QSTK.qstkutil': ['qstkutil/NYSE_dates.txt'],
    #                'QSTK.qstktest': ['qstktest/*.csv'],
    #                'QSTK.qstkstudy': ['qstkstudy/sp500.txt']},
    packages=find_packages(),
    namespace_packages=['QSTK'],
    include_package_data=True,
    long_description=open('README.md').read(),
    author_email='sourabhbajaj90@gmail.com',
    url='http://wiki.quantsoftware.org',
    license=open('LICENSE.txt').read(),
    description='QuantSoftware Toolkit',
    # data_files=[('QSData', ['QSData/Yahoo/*.csv',
    #                         'QSData/Yahoo/Lists/*.txt']),
    #             ('qstkutil', ['qstkutil/NYSE_dates.txt'])],
    # data_files=gen_data_files("bin", "Examples", "QSTK"),
    install_requires=[
        "numpy >= 1.6.1",
        "scipy >= 0.9.0",
        "matplotlib >= 1.1.0",
        "pandas==0.7.3",
        "python-dateutil >= 1.5",
        "cvxopt >= 1.1.3",
        "scikit-learn >= 0.11",
    ],
)
