#include <openssl/err.h>
#include <openssl/ssl.h>
#include <openssl/engine.h>

void report_error(const char* msg) {
    printf("Failing calling: %s\n", msg);
    printf("Error: %s\n", ERR_reason_error_string(ERR_get_error()));
    abort(); // failed
}

EVP_PKEY* load_key()
{
    ENGINE_load_builtin_engines();
    ENGINE_load_dynamic();
    ENGINE *eng = ENGINE_by_id("dynamic");
    if (!eng) {
        report_error("ENGINE_by_id");
    }
    if (!ENGINE_ctrl_cmd_string(eng, "ID", "pkcs11", 0)) {
        report_error("load pkcs11");
    }
    if (!ENGINE_ctrl_cmd_string(eng, "SO_PATH", "/usr/lib/x86_64-linux-gnu/engines-1.1/libpkcs11.so", 0)) {
        report_error("load SO path");
    }
    if (!ENGINE_ctrl_cmd_string(eng, "LOAD", NULL, 0)) {
        report_error("call LOAD");
    }
    if (!ENGINE_ctrl_cmd_string(eng, "MODULE_PATH", "/usr/local/lib/softhsm/libsofthsm2.so", 0)) {
        report_error("load MODULE path");
    }
    if (!ENGINE_init(eng)) {
        report_error("init engine");
    }
    
    EVP_PKEY *key = ENGINE_load_private_key(eng, "pkcs11:token=token1;object=rsaclient;pin-value=mynewpin", NULL, NULL);

    if (!key) {
        report_error("load private key");
    }

    return key;
}

void* load_key2()
{
    ENGINE_load_dynamic();
    ENGINE* engine = ENGINE_by_id("pkcs11");
    if (!engine) {
        report_error("ENGINE_by_id");
    }
    if (!ENGINE_set_default(engine, ENGINE_METHOD_ALL)) {
      report_error("ENGINE_set_default");
    }
    if (!ENGINE_init(engine)) {
        report_error("ENGINE_init");
    }
    EVP_PKEY *private_key = ENGINE_load_private_key(engine, "pkcs11:token=token1;object=rsaclient;pin-value=mynewpin", 0, 0);
    if (!private_key) {
      report_error("ENGINE_load_private_key");
    }
    printf("private_key: %p\n", private_key);
    return private_key;
}

int use_key_cert(SSL_CTX *ctx)
{
    EVP_PKEY* key = load_key();
    if (!SSL_CTX_use_certificate_file(ctx, "./../rsa-client-cert.pem", 1)) {
        report_error("use cert file");
    }
    if (!SSL_CTX_use_PrivateKey(ctx, key)) {
        report_error("use private key");
    }

    return 1;
}

int use_key_cert2(void *ctx)
{
    printf("original_ctx is: %p\n", ctx);
    SSL_CTX *casted_ctx = (SSL_CTX *)ctx;
    printf("casted_ctx is: %p\n", casted_ctx);

    EVP_PKEY* key = load_key2();
    printf("after load key\n");
    if (!SSL_CTX_use_certificate_file(casted_ctx, "./../rsa-client-cert.pem", 1)) {
        report_error("use cert file");
    }
    printf("after use cert\n");
    if (!SSL_CTX_use_PrivateKey(casted_ctx, key)) {
        report_error("use private key");
    }

    return 1;
}