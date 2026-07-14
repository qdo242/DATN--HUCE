import time
import statistics
import json
import os
from Cryptodome.Cipher import AES
from xor_cipher import xor_encrypt, xor_decrypt, NETWORK_KEY as XOR_KEY

AES_KEY = b'key_x_1234567890'
PAYLOAD_SIZES = [50, 100, 200, 500, 1000]
ITERATIONS = 2000

def aes_encrypt(data: bytes) -> bytes:
    iv = os.urandom(16)
    padded_len = ((len(data) + 15) // 16) * 16
    pad = data.ljust(padded_len, b'\0')
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv=iv)
    ct = cipher.encrypt(pad)
    return iv + ct

def aes_decrypt(packet: bytes) -> bytes:
    iv = packet[:16]
    ct = packet[16:]
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv=iv)
    return cipher.decrypt(ct).rstrip(b'\0')

def xor_encrypt_wrapper(data: bytes) -> bytes:
    return xor_encrypt(data)

def xor_decrypt_wrapper(data: bytes) -> bytes:
    return xor_decrypt(data)

def bench(func, data, iters=ITERATIONS):
    times = []
    for _ in range(iters):
        t0 = time.perf_counter()
        func(data)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1_000_000)
    return statistics.mean(times), statistics.stdev(times), min(times), max(times)

results = []
for size in PAYLOAD_SIZES:
    pt = os.urandom(size)
    ct_aes = aes_encrypt(pt)
    ct_xor = xor_encrypt_wrapper(pt)

    mean_e, std_e, min_e, max_e = bench(aes_encrypt, pt)
    mean_d, std_d, min_d, max_d = bench(aes_decrypt, ct_aes)
    mean_xe, std_xe, min_xe, max_xe = bench(xor_encrypt_wrapper, pt)
    mean_xd, std_xd, min_xd, max_xd = bench(xor_decrypt_wrapper, ct_xor)

    results.append((size, mean_e, std_e, mean_d, std_d, mean_xe, std_xe, mean_xd, std_xd))
    print(f"Payload {size:5}B: AES enc={mean_e:8.2f}us dec={mean_d:8.2f}us | XOR enc={mean_xe:8.2f}us dec={mean_xd:8.2f}us")

print("\n=== BANG SO SANH CHI TIET ===")
header = f"{'Size':>6} | {'AES Enc(us)':>12} {'AES Dec(us)':>12} {'XOR Enc(us)':>12} {'XOR Dec(us)':>12} | {'Ty le AES/XOR':>14}"
print(header)
print("-" * len(header))
for size, me, se, md, sd, mxe, sxe, mxd, sxd in results:
    ratio = (me + md) / (mxe + mxd)
    print(f"{size:>6} | {me:>10.2f}us {md:>10.2f}us {mxe:>10.2f}us {mxd:>10.2f}us | {ratio:>12.1f}x")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
sizes_arr = np.array([r[0] for r in results])
aes_enc = np.array([r[1] for r in results])
aes_dec = np.array([r[3] for r in results])
xor_enc = np.array([r[5] for r in results])
xor_dec = np.array([r[7] for r in results])

x = np.arange(len(sizes_arr))
w = 0.2

ax1.bar(x - 1.5*w, aes_enc, w, label='AES Encrypt', color='#e74c3c')
ax1.bar(x - 0.5*w, aes_dec, w, label='AES Decrypt', color='#c0392b')
ax1.bar(x + 0.5*w, xor_enc, w, label='XOR Encrypt', color='#2ecc71')
ax1.bar(x + 1.5*w, xor_dec, w, label='XOR Decrypt', color='#27ae60')
ax1.set_xticks(x)
ax1.set_xticklabels([f'{s}B' for s in sizes_arr])
ax1.set_ylabel('Thoi gian (microseconds)')
ax1.set_title('So sanh toc do AES vs XOR')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

ax2.bar(x - 1.5*w, aes_enc + aes_dec, w, label='AES (Enc+Dec)', color='#e74c3c')
ax2.bar(x + 0.5*w, xor_enc + xor_dec, w, label='XOR (Enc+Dec)', color='#2ecc71')
ax2.set_xticks(x)
ax2.set_xticklabels([f'{s}B' for s in sizes_arr])
ax2.set_ylabel('Tong thoi gian (microseconds)')
ax2.set_title('So sanh tong thoi gian xu ly')
ax2.legend()
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'images', 'benchmark_crypto.png')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
plt.savefig(out_path, dpi=150)
print(f"\nDa luu bieu do: {out_path}")
plt.close()
