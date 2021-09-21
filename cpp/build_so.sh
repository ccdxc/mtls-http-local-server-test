rm -f my_functions.so
gcc -g -Wall -pthread -fPIC -shared -o my_functions.so so.c -lssl -lcrypto