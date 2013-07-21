#
# (c) 2011, 2012 Georgia Tech Research Corporation
# This source code is released under the New BSD license.  
# Please see http://wiki.quantsoftware.org/index.php?title=QSTK_License
# for license details.

# Created on Jan 16, 2013

# @author: Sourabh Bajaj
# @contact: sourabhbajaj90@gmail.com
# @summary: Ubuntu Installation script of QSTK
#

echo "Updating apt-get"
sudo apt-get update
# sudo apt-get upgrade
# echo "Installing dependency - GIT"
# sudo apt-get install git-core
echo "Installing dependencies - Numpy Scipy matplotlib"
sudo apt-get --yes --force-yes install python-numpy
sudo apt-get --yes --force-yes install python-scipy
sudo apt-get --yes --force-yes install python-matplotlib
echo "Installing dependencies - developer tools"
sudo apt-get --yes --force-yes install python-dev
sudo apt-get --yes --force-yes install python-setuptools
sudo apt-get --yes --force-yes install python-pip
echo "Installing dependencies - scikits"
sudo pip install scikits.statsmodels
sudo pip install scikit-learn
echo "Installing dependencies - pandas"
sudo pip install pandas
# echo "Installing dependencies - PYQT4"
# sudo apt-get install python-qt4
echo "Installing dependencies - CVXOPT"
sudo apt-get --yes --force-yes build-dep python-cvxopt
sudo apt-get --yes --force-yes install python-cvxopt
echo "Install Unzip"
sudo apt-get --yes --force-yes install unzip

echo "Installing dependencies complete"
