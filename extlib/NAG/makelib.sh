#!/bin/sh

nagcdir=/nethome/jcornwell6/NAG/cll6a09dhl

gcc -shared -I /usr/local/lib/python2.6/site-packages/numpy/core/include/numpy/ -I /usr/local/include/python2.6/ \
 -lpython2.6 -I${nagcdir}/include -fPIC nagint.c ${nagcdir}/lib/libnagc_nag.a -o nagint.so

