def first_way_to_load(key_id):
    # This way we need to set the engine path:
    # export OPENSSL_ENGINES=/usr/lib/x86_64-linux-gnu/engines-1.1
    from OpenSSL._util import (
        ffi as _ffi,
        lib as _lib,
    )

    null = _ffi.NULL

    _lib.ENGINE_load_builtin_engines()
    e = _lib.ENGINE_by_id(b"pkcs11")
    if not e:
        raise ValueError("failed to load engine")
    if not _lib.ENGINE_init(e):
        raise ValueError("failed to init engine: ")

    key = _lib.ENGINE_load_private_key(e, key_id, null, null)
    if not key:
        raise ValueError("failed to load private key: ")

    return key


def second_way_to_load(key_id):
    # This way we don't set the engine path
    from OpenSSL._util import (
        ffi as _ffi,
        lib as _lib,
    )

    null = _ffi.NULL

    _lib.ENGINE_load_builtin_engines()
    e = _lib.ENGINE_by_id(b"dynamic")
    if not e:
        raise ValueError("failed to load engine")
    if not _lib.ENGINE_ctrl_cmd_string(e, b"ID", b"pkcs11", 0):
        raise ValueError("failed to set ID")
    if not _lib.ENGINE_ctrl_cmd_string(e, b"SO_PATH", b"/usr/lib/x86_64-linux-gnu/engines-1.1/libpkcs11.so", 0):
        raise ValueError("failed to set dynamic_path")
    if not _lib.ENGINE_ctrl_cmd_string(e, b"LOAD", null, 0):
        raise ValueError("cannot LOAD")
    if not _lib.ENGINE_ctrl_cmd_string(e, b"MODULE_PATH", b"/usr/local/lib/softhsm/libsofthsm2.so", 0):
        raise ValueError("failed to set MODULE_PATH")
    if not _lib.ENGINE_init(e):
        raise ValueError("failed to init engine: ")

    key = _lib.ENGINE_load_private_key(e, key_id, null, null)
    if not key:
        raise ValueError("failed to load private key: ")

    return key

if __name__ == "__main__":
    print(second_way_to_load(b"pkcs11:token=token1;object=mtlskey;pin-value=mynewpin"))