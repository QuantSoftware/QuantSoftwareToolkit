#
# (c) 2011, 2012 Georgia Tech Research Corporation
# This source code is released under the New BSD license.  Please see
# http://wiki.quantsoftware.org/index.php?title=QSTK_License
# for license details.

# Created on Jan 16, 2013

# @author: Sourabh Bajaj
# @contact: sourabhbajaj90@gmail.com
# @summary: Ubuntu Installation script of QSTK
#

echo "Updating apt-get"
sudo apt-get update
sudo apt-get upgrade
echo "Installing dependency - GIT"
sudo apt-get install git-core
echo "Installing dependencies - Numpy Scipy matplotlib"
sudo apt-get install python-numpy
sudo apt-get install python-scipy
sudo apt-get install python-matplotlib
echo "Installing dependencies - developer tools"
sudo apt-get install python-dev
sudo apt-get install python-setuptools
echo "Installing dependencies - scikits"
sudo easy_install -U scikits.statsmodels
sudo easy_install -U scikits-learn
sudo easy_install --upgrade pytz
sudo apt-get install python-dateutil
echo "Installing dependencies - pandas"
sudo easy_install pandas==0.7.3
echo "Installing dependencies - PYQT4"
sudo apt-get install python-qt4
echo "Installing dependencies - CVXOPT"
sudo apt-get build-dep python-cvxopt
sudo apt-get install python-cvxopt
echo "Installing dependencies complete"
