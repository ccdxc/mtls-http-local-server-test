### generate cert/keys

First make sure we have the cert/keys in SoftHSM and the upper directory.

```
cd ..
. ./init_hsm.sh
```

Then we set the SOFTHSM2_CONF to the full path.
```
export SOFTHSM2_CONF=/full/path/to/upper/directory/softhsm.conf
```

### bring up a local openssl server

Then bring up a local OpenSSL server. Choose `rsa{ec}-client-cert.pem` in `-CAfile` for RSA/EC tests.

```bash
openssl s_server -cert rsa-server-cert.pem -key rsa-server-key.pem \
    -CAfile rsa-client-cert.pem \
    -WWW -port 12345 -verify_return_error -Verify 1
```

### run the client code

Now open a new tab, and go to the `cpp` folder, and set SOFTHSM2_CONF.
```
export SOFTHSM2_CONF=/full/path/to/upper/directory/softhsm.conf
```

Run `build_so.sh` to compile `so.c` into a `my_functions.so` shared library. `so.c` has a 
`int use_rsa_key_cert(SSL_CTX *ctx)` function which writes the RSA cert and RSA key (from
HSM) into the given SSL_CTX, and returns 1 if succeeded. Similarly there is a `use_ec_key_cert`
function. Right now we are hardcoding the cert path and key id in `so.c`, we will figure out
how to pass cert bytes and key id to these functions in the future.

Now you can run `python load_so.py` to test these functions. You should see two `1`'s indicating
both functions return 1.

Now you can run end to end test with `sample.py`. `sample.py` loads the `my_functions.so` and 
call these functions. Choose `do_test(True)`
for RSA key and `do_test(False)` for EC key in `sample.py`, and run `sample.py`. You should 
see the 200 status.