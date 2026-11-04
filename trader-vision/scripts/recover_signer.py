#!/usr/bin/env python3
"""Recover the *same* Android signing key. Requires owner's private recovery kit.

Dependencies: pip install cryptography
Usage:
  python trader-vision/scripts/recover_signer.py --backup keystore-vc3-permanent.encrypted.json --private recovery-private-encrypted.pem --output-dir /secure/local/trader-signer
The passphrase prompt must be answered using the offline recovery kit.
Never commit the recovered PKCS12/password and never print passwords in logs.
"""
import argparse
import base64
import getpass
import json
import os
import re
import subprocess
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PINNED_CERT = "e52d1c13baa3a4e7f73b71cb7e15bc1fdd8709650aa64fe8a9b86bb26a5491f9"
PACKAGE = "pt.vcaitano.tradervision.gestaoteste"
AAD = b"VOC-TRADER-VISION-SIGNING-V1"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    encrypted = json.loads(args.backup.read_text(encoding="utf-8"))
    if encrypted.get("algorithm") != "RSA-OAEP-SHA256+AES-256-GCM":
        raise RuntimeError("Unsupported signing backup")
    if encrypted.get("certificateSha256") != PINNED_CERT or encrypted.get("packageName") != PACKAGE:
        raise RuntimeError("Signing backup doesn't match pinned application")
    pwd = getpass.getpass("Senha de recuperacao (nao aparecera): ").encode("utf-8")
    private = serialization.load_pem_private_key(args.private.read_bytes(), password=pwd)
    key = private.decrypt(
        base64.b64decode(encrypted["encryptedKey"]),
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    plain = AESGCM(key).decrypt(base64.b64decode(encrypted["nonce"]),
                                base64.b64decode(encrypted["ciphertext"]), AAD)
    payload = json.loads(plain)
    if payload.get("packageName") != PACKAGE or payload.get("certificateSha256") != PINNED_CERT:
        raise RuntimeError("Decrypted identity doesn't match pinned certificate")
    key_bytes = base64.b64decode(payload["keystorePkcs12Base64"], validate=True)
    password = payload["keystorePassword"]
    if not key_bytes or not password or payload["keyAlias"] != "voc-trader-release":
        raise RuntimeError("Invalid recovered key data")
    args.output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(args.output_dir, 0o700)
    store = args.output_dir / "voc-trader-permanent-vc3.p12"
    passwd = args.output_dir / "voc-trader-permanent-password.txt"
    store.write_bytes(key_bytes)
    passwd.write_text(password, encoding="utf-8")
    os.chmod(store,0o600)
    os.chmod(passwd,0o600)
    try:
        result = subprocess.run(
            ["keytool","-list","-v","-storetype","PKCS12","-keystore",str(store),
             "-alias","voc-trader-release","-storepass",password],
            check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True
        )
        hashes_found=re.findall(r"SHA256:\\s*([0-9A-Fa-f:]+)",result.stdout)
        if not hashes_found or hashes_found[0].replace(":","").lower() != PINNED_CERT:
            raise RuntimeError("Recovered keystore certificate DOES NOT MATCH VC3")
    except Exception:
        store.unlink(missing_ok=True)
        passwd.unlink(missing_ok=True)
        raise
    print("Recovered original VC3 signer and verified exact certificate SHA-256:",PINNED_CERT)
    print("Keystore local:",store)
    print("Password local:",passwd)
    print("Remove these files when the signed release has been verified.")
if __name__=="__main__":
    main()
