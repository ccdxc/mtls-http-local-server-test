export SOFTHSM2_CONF=./softhsm.conf

rm -rf tokens/*

echo "============ initializing softhsm"

pkcs11-tool --module /usr/local/lib/softhsm/libsofthsm2.so --slot-index=0 --init-token --label="token1" --so-pin="123456"
pkcs11-tool --module /usr/local/lib/softhsm/libsofthsm2.so  --label="token1" --init-pin --so-pin "123456" --pin mynewpin


echo "============ writing EC keys into softhsm, label: mtlskey, id: 1111"

pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object key.pem --type privkey --id 1111 --label mtlskey --slot-index 0
pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object cert.pem --type cert --id 1111 --label mtlskey --slot-index 0

echo "============ generating RSA keys for openssl local server"

# generate RSA cert/key for openssl server
openssl req -nodes -x509 -newkey rsa:4096 -keyout rsa-server-key.pem -out rsa-server-cert.pem -days 3650 -subj '/CN=localhost'

echo "============ generating RSA keys for client"

# generate RSA cert/key for client
openssl req -nodes -x509 -newkey rsa:4096 -keyout rsa-client-key.pem -out rsa-client-cert.pem -days 3650 -subj '/CN=my-mtls-test'

echo "============ writing RSA client keys into softhsm, label: rsaclient, id: 2222"

# Write RSA cert/key to HSM, label is "rsaclient"
pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object rsa-client-key.pem --type privkey --id 2222 --label rsaclient --slot-index 0
pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object rsa-client-cert.pem --type cert --id 2222 --label rsaclient --slot-index 0


echo "============ generating self signed EC keys for client"
openssl ecparam -noout -name prime256v1 -genkey -out ec-client-key.pem -outform PEM
openssl req -new -x509 -key ec-client-key.pem -out ec-client-cert.pem -days 730 -subj '/CN=my-mtls-test-ec-key'

echo "============ writing self signed EC client keys into softhsm, label: ecclient, id: 3333"

# Write RSA cert/key to HSM, label is "rsaclient"
pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object ec-client-key.pem --type privkey --id 3333 --label ecclient --slot-index 0
pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object ec-client-cert.pem --type cert --id 3333 --label ecclient --slot-index 0