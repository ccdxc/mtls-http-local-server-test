import ctypes
import cffi
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

so_file = "./my_functions.so"
ffi = cffi.FFI()
my_functions = ctypes.CDLL(so_file)

# RSA cert/key

use_rsa_key_cert = my_functions.use_rsa_key_cert
use_rsa_key_cert.argtypes = [ctypes.c_void_p]

ctx_rsa = create_urllib3_context()
ctx_rsa_ptr = ctypes.cast(int(ffi.cast("intptr_t", ctx_rsa._ctx._context)), ctypes.c_void_p)
print(use_rsa_key_cert(ctx_rsa_ptr))

# EC cert/key

use_ec_key_cert = my_functions.use_ec_key_cert
use_ec_key_cert.argtypes = [ctypes.c_void_p]

ctx_ec = create_urllib3_context()
ctx_ec_ptr = ctypes.cast(int(ffi.cast("intptr_t", ctx_ec._ctx._context)), ctypes.c_void_p)
print(use_ec_key_cert(ctx_ec_ptr))