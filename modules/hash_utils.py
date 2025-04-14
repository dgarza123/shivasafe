import hashlib

def compute_sha256_hash(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()
