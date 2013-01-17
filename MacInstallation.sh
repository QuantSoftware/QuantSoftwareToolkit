#
# (c) 2011, 2012 Georgia Tech Research Corporation
# This source code is released under the New BSD license.  Please see
# http://wiki.quantsoftware.org/index.php?title=QSTK_License
# for license details.

# Created on Jan 16, 2013

# @author: Sourabh Bajaj
# @contact: sourabhbajaj90@gmail.com
# @summary: Mac Installation script of QSTK
#

echo "Installing dependency - GIT"
sudo port install git-core +svn
sudo port install python27
echo "Installing dependencies - Numpy Scipy matplotlib"
sudo port install py27-numpy
sudo port install py27-scipy
sudo port install py27-matplotlib
echo "Installing dependencies - developer tools"
sudo port install py27-dateutil
echo "Installing dependencies - scikits"
sudo easy_install -U scikits-learn
echo "Installing dependencies - pandas"
sudo easy_install pandas==0.7.3
echo "Installing dependencies - Docs/Distribute"
sudo port install py27-epydoc
sudo port install py27-distribute
echo "Installing dependencies - PYQT4"
sudo port install py27-pyqt4
echo "Installing dependencies - CVXOPT"
sudo port install py27-cvxopt
echo "Installing dependencies complete"
