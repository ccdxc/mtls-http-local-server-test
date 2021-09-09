# PKCS11 Codelab using local OpenSSL mtls server

## Download the codelab and its dependencies

```bash
# Clone the codelab repo
git clone https://github.com/arithmetic1728/mtls-http-local-server-test.git

cd mtls-http-local-server-test

# Create and activate a Python virtual environment
pyenv virtualenv my_env
pyenv local my_env

# Install the dependencies.
python -m pip install -r requirements.txt
```

## Install openssl with pkcs11

First install openssl with its [PKCS11 engine](https://github.com/OpenSC/libp11#openssl-engines).

```bash
# add to /etc/apt/sources.list
  deb http://http.us.debian.org/debian/ testing non-free contrib main

# then
export DEBIAN_FRONTEND=noninteractive 
apt-get update && apt-get install libtpm2-pkcs11-1 tpm2-tools libengine-pkcs11-openssl opensc -y
```

Note, the installation above adds in the libraries for all modules in this repo (TPM, OpenSC, etc)..you may only need `libengine-pkcs11-openssl` here to verify

Once installed, you can check that it can be loaded:

Set the pkcs11 provider and module directly into openssl (make sure `libpkcs11.so` engine reference exists first!)

- `/etc/ssl/openssl.cnf`
```bash
openssl_conf = openssl_def
[openssl_def]
engines = engine_section

[engine_section]
pkcs11 = pkcs11_section

[pkcs11_section]
engine_id = pkcs11
dynamic_path = /usr/lib/x86_64-linux-gnu/engines-1.1/libpkcs11.so
```

---

## SOFTHSM

SoftHSM is as the name suggests, a sofware "HSM" module used for testing.   It is of course not hardware backed but the module does allow for a PKCS11 interface which we will also use for testing.

First install the softhsm library.

- [SoftHSM Install](https://www.opendnssec.org/softhsm/)

Next in this codelab, create a `tokens` folder.
```bash
mkdir tokens
```

Then open the `softhsm.conf` file, and set the `directories.tokendir` value to the absolute path of the
`tokens` folder. This way SoftHSM will save 
tokens into the `./tokens/` folder.

```bash
# softhsm.conf content looks like this
log.level = DEBUG
objectstore.backend = file
directories.tokendir = /absolute/path/of/tokens/folder/
slots.removable = true
```

Now, make sure that the installation created the softhsm module for openssl:  `[PATH]/libsofthsm2.so`. My softhsm
module is at: `/usr/local/lib/softhsm/libsofthsm2.so`.

## Generate mTLS certs

At this point, we can generate mTLS certificate and private key, and import private key into SoftHSM.

```bash
/opt/google/endpoint-verification/bin/apihelper --print_certificate
```

This command will print out the following:
```
-----BEGIN CERTIFICATE-----
<omitted>
-----END CERTIFICATE-----
-----BEGIN PRIVATE KEY-----
<omitted>
-----END PRIVATE KEY-----
```

Copy the private key and certificate into a key.pem and cert.pem file.

## Initialize SoftHSM

Run the following script:

```bash
. ./init_hsm.sh
```

This script does the following things:
- write the key.pem into SoftHSM using label "mtlskey" and id "1111".
- create RSA server cert/key
- create RSA client cert/key and write the client key into SoftHSM with label "rsaclient" and id "2222".


## Run the sample application

First bring up a local OpenSSL mtls server. The server uses `rsa-server-cert.pem` and `rsa-server-key.pem`
as the server side SSL credentials. The `-CAfile` is used to specify the CA file to verify client's cert, so
it depends on which client side cert you want to use.

If you want to use the real cert/key generated from `apihelper`, then use `cert.pem` as the `-CAfile`; 
if you want to test the self signed RSA cert/key, then use `rsa-client-cert.pem` as the `-CAfile`. 

```bash
openssl s_server -cert rsa-server-cert.pem -key rsa-server-key.pem \
    -CAfile rsa-client-cert.pem \
    -WWW -port 12345 -verify_return_error -Verify 1
```

Next open a new tab. Open `sample.py` and choose the cert you want to test. Then run

```bash
export SOFTHSM2_CONF=./softhsm.conf

python sample.py
```

Ignore the warning. If you use RSA client cert, then you should see a `200` status code.