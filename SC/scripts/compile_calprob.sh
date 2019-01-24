cython cal_prob.pyx
gcc -c -O3 -fPIC -I/usr/include/python2.7 cal_prob.c
gcc -shared cal_prob.o -o cal_prob.so
