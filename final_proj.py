import numpy as np
import galois
import random
bits = 256

from collections import defaultdict
from collections import namedtuple


def keygen(bits):
    """Generates keys with `bits`-bits of security. Returns a pair: (secret key, public key)."""
    def invmod(x, m):
        gcd, s, t = galois.egcd(x, m)
        assert gcd == 1
        return s

    p = galois.random_prime(int(bits/2))
    q = galois.random_prime(int(bits/2))

    n = p*q
    g = n+1
    lamb = (p-1) * (q-1)
    mu = invmod(lamb, n)
    
    sk = (lamb, mu)
    pk = (n, g)
    return sk, pk

def encrypt(m, pk):
    """Encrypts the message `m` with public key `pk`."""
    n, g = pk
    n_sq = n**2
    r = random.randint(1, n)
    c = (pow(g, m, n_sq) * pow(r, n, n_sq)) % n_sq
    return c

def decrypt(c, sk, pk):
    """Decrypts the ciphertext `c` using secret key `sk` and public key `pk`."""
    lamb, mu = sk
    n, g = pk
    n_sq = n**2
    L_result = (pow(c, lamb, n_sq) - 1)//n
    return (L_result * mu) % n

def e_add(c1, c2, pk):
    """Add one encrypted integer to another"""
    n, g = pk

    return c1 * c2 % n**2


class Reporter:
    def report(self, m_salaries, w_salaries, server):
        """Submits encrypted salaries to server"""
        pk = server.get_public_key()

        # Encrypt salaries
        enc_w_salaries = [encrypt(salary, pk) for salary in w_salaries]
        enc_m_salaries = [encrypt(salary, pk) for salary in m_salaries]

        # Send to server
        server.submit_w_salaries(enc_w_salaries)
        server.submit_m_salaries(enc_m_salaries)

class TallyServer:
    def __init__(self):
        self.m_salaries = []
        self.w_salaries = []
        self.sk, self.pk = keygen(32)
    
    def get_public_key(self):
        """Get the public key from the election server"""
        return self.pk

    def submit_w_salaries(self, w_salaries):
        """Submit encrypted w_salaries to the server"""
        for salary in w_salaries:
	        self.w_salaries.append(salary)
    
    def submit_m_salaries(self, m_salaries):
        """Submit encrypted m_salaries to the server"""
        for salary in m_salaries:
	        self.m_salaries.append(salary)
    
    def tally_salaries(self):
	    """Tally up the salaries after all reporting. Returns average salaries for both sexes."""
	    
	    # Encrypted totals
	    enc_m_total = encrypt(0, self.pk)
	    enc_w_total = encrypt(0, self.pk)

	    # Add m_salaries
	    for salary in self.m_salaries:
	        enc_m_total = e_add(enc_m_total, salary, self.pk)

	    # Add w_salaries
	    for salary in self.w_salaries:
	        enc_w_total = e_add(enc_w_total, salary, self.pk)

	    # Decrypt totals
	    m_total = decrypt(enc_m_total, self.sk, self.pk)
	    w_total = decrypt(enc_w_total, self.sk, self.pk)

	    # Calculate averages
	    m_avg = m_total / len(self.m_salaries)
	    w_avg = w_total / len(self.w_salaries)

	    return m_avg, w_avg

server = TallyServer()

# random ranges to simulate different amounts of male/female employees per company
r1 = random.randint(10, 50)
r2 = random.randint(10, 50)
r3 = random.randint(10, 50)
r4 = random.randint(10, 50)
r5 = random.randint(10, 50)
r6 = random.randint(10, 50)

r_m_total = r1 + r2 + r3
r_w_total = r4 + r5 + r6

m1 = [random.randint(95000, 150000) for _ in range(r1)]
m2 = [random.randint(65000, 95000) for _ in range(r2)]
m3 = [random.randint(25000, 65000) for _ in range(r3)]

w1 = [random.randint(95000, 150000) for _ in range(r4)]
w2 = [random.randint(65000, 95000) for _ in range(r5)]
w3 = [random.randint(25000, 65000) for _ in range(r6)]

Reporter().report(m1, w1, server)
Reporter().report(m2, w2, server)
Reporter().report(m3, w3, server)

real_m_total = np.sum(m1) + np.sum(m2) + np.sum(m3)
real_w_total = np.sum(w1) + np.sum(w2) + np.sum(w3)

real_m_avg = real_m_total / r_m_total
real_w_avg = real_w_total / r_w_total

tallied_m_avg, tallied_w_avg = server.tally_salaries()

assert real_m_avg == tallied_m_avg
assert real_w_avg == tallied_w_avg
print("Success!")
print(f'real m_avg:{real_m_avg:.2f}, tallied w_avg: {tallied_m_avg:.2f}')
print(f'real w_avg:{real_w_avg:.2f}, tallied w_avg: {tallied_w_avg:.2f}')







