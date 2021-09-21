import requests
from requests.adapters import HTTPAdapter
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
from requests.packages.urllib3.poolmanager import PoolManager
import ctypes
import cffi
ffi = cffi.FFI()


class HsmAdapter(HTTPAdapter):
    def __init__(self, use_rsa=True):
        self.use_rsa = use_rsa
        super(HsmAdapter, self).__init__()
    
    def _add_cert_key(self, ctx):
        so_file = "./my_functions.so"
        
        my_functions = ctypes.CDLL(so_file)

        if self.use_rsa:
            use_rsa_key_cert = my_functions.use_rsa_key_cert
            use_rsa_key_cert.argtypes = [ctypes.c_void_p]

            ctx_ptr = ctypes.cast(int(ffi.cast("intptr_t", ctx._ctx._context)), ctypes.c_void_p)
            print(use_rsa_key_cert(ctx_ptr))
        else:
            use_ec_key_cert = my_functions.use_ec_key_cert
            use_ec_key_cert.argtypes = [ctypes.c_void_p]

            ctx_ptr = ctypes.cast(int(ffi.cast("intptr_t", ctx._ctx._context)), ctypes.c_void_p)
            print(use_ec_key_cert(ctx_ptr))

    def init_poolmanager(self, connections, maxsize, block=False, *args, **kwargs):
        from OpenSSL._util import lib as _lib
        from OpenSSL._util import exception_from_error_queue as _exception_from_error_queue
        _lib.SSL_load_error_strings()

        context = create_urllib3_context()

        # load CA files, we use the server cert as the CA file since it is self signed
        context.load_verify_locations(cafile="./../rsa-server-cert.pem")

        self._add_cert_key(context)
        
        kwargs['ssl_context'] = context
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, *args, **kwargs)


def do_test(use_rsa):
    s = requests.Session()

    s.mount("https://", HsmAdapter(use_rsa))
    res = s.get("https://localhost:12345")
    print(res.status_code)


if __name__ == "__main__":
    # uncomment for RSA key
    #do_test(True)

    # uncomment for EC key
    #do_test(False)
    
    pass