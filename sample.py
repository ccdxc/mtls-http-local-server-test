from util import second_way_to_load

import certifi
import requests
from requests.adapters import HTTPAdapter
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
from requests.packages.urllib3.poolmanager import PoolManager


class HsmAdapter(HTTPAdapter):
    def __init__(self, cert_path, key_id):
        self.cert_path = cert_path
        self.key_id = key_id
        super(HsmAdapter, self).__init__()

    def init_poolmanager(self, connections, maxsize, block=False, *args, **kwargs):
        from OpenSSL import crypto
        from OpenSSL._util import lib as _lib
        from OpenSSL._util import exception_from_error_queue as _exception_from_error_queue
        _lib.SSL_load_error_strings()

        context = create_urllib3_context()
        ctx = context._ctx._context

        # load CA files, we use the server cert as the CA file since it is self signed
        context.load_verify_locations(cafile="./rsa-server-cert.pem")

        # load certificate
        if not _lib.SSL_CTX_use_certificate_file(ctx, self.cert_path.encode(), 1):
            _exception_from_error_queue(Exception)

        # load private key
        key = second_way_to_load(self.key_id)
        if not key:
            _exception_from_error_queue(Exception)
        if not _lib.SSL_CTX_use_PrivateKey(context._ctx._context, key):
            _exception_from_error_queue(Exception)
        
        kwargs['ssl_context'] = context
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, *args, **kwargs)


def do_test(cert_path, key_id):
    s = requests.Session()

    s.mount("https://", HsmAdapter(cert_path, key_id))
    res = s.get("https://localhost:12345")
    print(res.status_code)


if __name__ == "__main__":
    do_test("./rsa-client-cert.pem", b"pkcs11:token=token1;object=rsaclient;pin-value=mynewpin")
    #do_test("./cert.pem", b"pkcs11:token=token1;object=mtlskey;pin-value=mynewpin")