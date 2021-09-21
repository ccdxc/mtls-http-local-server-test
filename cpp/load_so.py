import ctypes
import cffi
so_file = "./my_functions.so"
ffi = cffi.FFI()

my_functions = ctypes.CDLL(so_file)
use_key_cert2 = my_functions.use_key_cert2
use_key_cert2.argtypes = [ctypes.c_void_p]

load_key2 = my_functions.load_key2

import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

ctx = create_urllib3_context()
print(type(ctx._ctx))
ctx_ptr = ctypes.cast(int(ffi.cast("intptr_t", ctx._ctx._context)), ctypes.c_void_p)
print(use_key_cert2(ctx_ptr))