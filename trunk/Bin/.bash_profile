# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

# User specific environment and startup programs

PATH=$HOME/bin:/usr/local/bin/:/usr/bin:$PATH:.
export PATH

PYTHONPATH=/usr/local/lib/python2.6/site-packages/:/usr/lib/python2.6/site-packages/:$PYTHONPATH:.

source ~/QSTK/local.sh
