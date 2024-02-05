

# This file was *autogenerated* from the file app.sage
from sage.all_cmdline import *   # import sage library

_sage_const_256 = Integer(256); _sage_const_4197821 = Integer(4197821); _sage_const_1 = Integer(1); _sage_const_3 = Integer(3); _sage_const_2 = Integer(2); _sage_const_8 = Integer(8); _sage_const_4 = Integer(4); _sage_const_5 = Integer(5); _sage_const_9 = Integer(9); _sage_const_10 = Integer(10); _sage_const_23 = Integer(23); _sage_const_0 = Integer(0); _sage_const_16 = Integer(16); _sage_const_29 = Integer(29); _sage_const_38 = Integer(38); _sage_const_32 = Integer(32); _sage_const_12 = Integer(12); _sage_const_14 = Integer(14)
import hashlib
import json
import time
from flask import Flask, request, render_template, flash, url_for, redirect, jsonify
import os
import database
import local_enc
import base64
import random
import string
from sm3 import *

from concurrent.futures import *
from hashlib import sha256, sha512
from typing import List
from gmpy2 import fac
from sage.stats.distributions.discrete_gaussian_polynomial import     DiscreteGaussianDistributionPolynomialSampler as d_gauss

class MusigL(object):
    N = _sage_const_256 
    q = _sage_const_4197821 
    Zq = GF(q)
    Rqx = PolynomialRing(Zq, names=('a',)); (a,) = Rqx._first_ngens(1)
    Rzx = PolynomialRing(ZZ, names=('b',)); (b,) = Rzx._first_ngens(1)
    Rrx = PolynomialRing(RR, names=('c',)); (c,) = Rrx._first_ngens(1)
    Rq = Rqx.quotient(a ** N + _sage_const_1 , 'x')
    R = Rzx.quotient(b ** N + _sage_const_1 , 'x')
    R_ = Rrx.quotient(c ** N + _sage_const_1 , 'x')

    def __init__(self, numbers):
        self.n = numbers
        self.m = _sage_const_3 

        self.omega = int(self.q.log(_sage_const_2 )) + _sage_const_1 
        self.k = _sage_const_8 
        self.l = _sage_const_4 
        self.eta = _sage_const_1 

        self.sigma_b = _sage_const_2  ** (_sage_const_5  / _sage_const_2 ) / sqrt(pi) * _sage_const_2  ** (_sage_const_2  / (self.N * self.k)) * self.N ** (_sage_const_3  / _sage_const_2 ) * sqrt(self.k * self.omega + _sage_const_1 )
        self.sigma_y = _sage_const_2  ** _sage_const_9  / (pi * sqrt(pi)) * _sage_const_2  ** (_sage_const_2  / (self.N * self.k)) * self.q ** (self.k / (self.l + self.k)) * self.N ** _sage_const_2  * sqrt(
            (self.k * self.omega + _sage_const_1 ) * (_sage_const_2  + self.N + ((self.l + self.k) * self.N).log(_sage_const_10 )))
        self.sigma_1 = self.sigma_b * (self.sigma_y) * sqrt(self.N * (_sage_const_2  * self.k * self.omega + _sage_const_1 ) * (self.l + self.k))

        self.B = self.sigma_1 * sqrt(self.N * (self.l + self.k))
        self.Bn = sqrt(self.n) * self.B

        self.kappa = _sage_const_23 
        self.T = self.kappa ** _sage_const_2  * self.eta * sqrt(self.N * (self.l + self.k))
        self.alpha = (self.sigma_1 - _sage_const_1 ) / self.T
        self.t = sqrt(self.N / ((pi - _sage_const_1 ) * log(e, _sage_const_2 )))
        self.M = exp(pi / self.alpha ** _sage_const_2  + (pi * self.t) / self.alpha)
        self.l_ = _sage_const_256 
        self.A_ = self.Setup()

    def norm2(self, array):
        num = _sage_const_0 
        coe = []
        for poly in array:
            poly = (poly.lift()).change_ring(ZZ)
            coe.extend(poly.coefficients())
        for i in coe:
            num += int((i + self.q // _sage_const_2 ) % self.q - self.q // _sage_const_2 ) ** _sage_const_2 
        return sqrt(num)

    def combine(seLf, a, b):
        if a < b: return _sage_const_0 
        return fac(int(a)) // (fac(int(b)) * fac(int(a - b)))

    def index(self, num: int, l1: int, l2: int, temp: List) -> List:
        if len(temp) == self.N:
            return temp
        if num < self.combine(l1 - _sage_const_1 , l2) * _sage_const_2  ** l2:
            temp = [_sage_const_0 ] + temp
            return self.index(num, l1 - _sage_const_1 , l2, temp)
        else:
            num -= self.combine(l1 - _sage_const_1 , l2) * _sage_const_2  ** l2
            if num < self.combine(l1 - _sage_const_1 , l2 - _sage_const_1 ) * _sage_const_2  ** (l2 - _sage_const_1 ):
                temp = [_sage_const_1 ] + temp
                return self.index(num, l1 - _sage_const_1 , l2 - _sage_const_1 , temp)
            else:
                num -= self.combine(l1 - _sage_const_1 , l2 - _sage_const_1 ) * _sage_const_2  ** (l2 - _sage_const_1 )
                temp = [-_sage_const_1 ] + temp
                return self.index(num, l1 - _sage_const_1 , l2 - _sage_const_1 , temp)

    def Hagg(self, arg1, arg2):
        m = str(arg1) + str(arg2)
        temp = int(sha256(m.encode()).hexdigest(), _sage_const_16 )
        idx = temp % (self.combine(self.N, self.k) * _sage_const_2  ** self.k)
        return self.R(self.index(idx, self.N, self.k, []))

    def Hsig(self, arg1, arg2, arg3):
        m = str(arg1) + str(arg2) + str(arg3)
        temp = int(sha512(m.encode()).hexdigest(), _sage_const_16 )
        idx = temp % (self.combine(self.N, self.k) * _sage_const_2  ** self.k)
        return self.R(self.index(idx, self.N, self.k, []))

    def Hnon(self, arg1, arg2, arg3, r):
        m = str(arg1) + str(arg2) + str(arg3) + str(r)
        temp = int(sm3_hash(bytes_to_list(m.encode())), _sage_const_16 )
        temp = temp % _sage_const_2  ** (self.l_ - _sage_const_1 )
        return bin(temp)[_sage_const_2 :].rjust(self.l_, '0')

    def Setup(self):
        A = random_matrix(self.Rq, self.k, self.l)
        self.A_=block_matrix([[A,matrix.identity(self.k)]])
        return self.A_

    def small_poly(self, sign=None, seed = None):
        if sign:
            set_random_seed(seed)
        f = []
        for i in range(_sage_const_256 ):
            f.append(randint(-_sage_const_1 , _sage_const_1 ))
        return self.R(f)

    def Gen(self, seed):
        skl = [list(self.small_poly(True, seed)) for i in range(self.k + self.l)]
        sk0 = vector(self.Rq, [self.Rq(i) for i in skl])
        pk = self.A_ * sk0
        sk = vector(self.R, [self.R(i) for i in skl])
        return pk, sk

    def Agg(self, on):
        for i in range(len(on)):
            if not on[i][_sage_const_0 ]:
                return None
        z = sum([on[i][_sage_const_0 ] for i in range(len(on))])
        w = on[_sage_const_0 ][_sage_const_1 ]
        z_ = []
        for i in z:
            z_.append(self.Rq(i.lift()))
        return w, vector(self.Rq, z_)

    def KAgg(self, L):
        t_ = _sage_const_0 
        for i in range(len(L)):
            t_ += self.Rq(self.Hagg(self.order(L), L[i]).lift()) * L[i]
        return t_

    def Ver(self, pk, sigma, miu):
        w_, z = sigma
        t_ = pk
        c = self.Rq(self.Hsig(w_, miu, t_).lift())
        if self.A_ * z - c * t_ == w_ and self.norm2(list(z)) <= self.Bn:
            return True
        else:
            return False

    def gauss_v(self, sigma, length):
        def arr_append(j):
            v[j] = d()
            v_[j] = list(v[j])

        d = d_gauss(self.R, self.N, sigma)
        v = [None] * length
        v_ = [None] * length

        pool = ThreadPoolExecutor(max_workers=_sage_const_4 )
        all_task = []
        for i in range(length):
            all_task.append(pool.submit(arr_append, i))
        wait(all_task, return_when=ALL_COMPLETED)
        pool.shutdown()

        return vector(self.R, v), v_

    def Samp(self, r, choice):
        set_random_seed(r)
        if choice:
            p = d_gauss(self.Rq, self.N, self.sigma_b)
        else:
            p = d_gauss(self.R, self.N, self.sigma_b)
        return p()

    def RejSamp(self, v, z, b):
        def ComputeN1():
            N1=_sage_const_0 
            for row in sz:
                f = row[_sage_const_0 ].lift()
                arr = f.coefficients()
                brr = []
                for i in range(len(arr)):
                    brr.append((arr[i] % self.q) ** _sage_const_2 )
                N1 += sum(brr)
            return N1
        def ComputeN2():
            N2=_sage_const_0 
            for row in szc:
                f = row[_sage_const_0 ].lift()
                arr = f.coefficients()
                brr = []
                for i in range(len(arr)):
                    brr.append((arr[i]) ** _sage_const_2 )
                N2 += sum(brr).lift()
            return N2

        Sigma = _sage_const_0 
        for ele in b:
            Sigma += ele ** _sage_const_2 

        Sigma = round(self.sigma_1 ** _sage_const_2 ) + Sigma * round(self.sigma_y ** _sage_const_2 )
        s_Sigma = matrix.identity(self.l + self.k)
        s_Sigma = matrix(self.Rq, s_Sigma)
        s_Sigma[_sage_const_0 , _sage_const_0 ] = Sigma ** (-_sage_const_1 )

        h_Sigma = round(self.sigma_1 ** _sage_const_2 ) * matrix.identity(self.l + self.k)
        sh_Sigma = h_Sigma.cholesky()

        z_ = matrix(self.Rrx, z).T
        z_ = matrix(self.R_, z_)
        sz = matrix(self.R_, sh_Sigma.inverse() * z_)

        tpl = list(z - v)
        tpv = []
        for i in tpl:
            tpv.append(self.Rq(i.lift()))
        temp = matrix(self.Rq, tpv).T
        szc = matrix(self.Rq, s_Sigma * temp)

        pool = ThreadPoolExecutor(max_workers=_sage_const_2 )
        all_task=[pool.submit(ComputeN1),pool.submit(ComputeN2)]

        set_random_seed()
        X = RealDistribution('uniform', [_sage_const_0 , _sage_const_1 ])
        lnrho = ln(X.get_random_element())

        wait(all_task, return_when=ALL_COMPLETED)
        N1=all_task[_sage_const_0 ].result()
        N2=all_task[_sage_const_1 ].result()
        pool.shutdown()

        lnPr = -pi * (N1 - N2) - ln(self.M)
        if lnrho >= min(_sage_const_0 , lnPr):
            return _sage_const_0 
        return _sage_const_1 

    def SignOff(self, A_, t):
        def arr_append(j):
            temp_arr[j] = self.gauss_v(self.sigma_y, self.l + self.k)
            y[j] = temp_arr[j][_sage_const_0 ]
            y_[j] = vector(self.Rq, [self.Rq(item) for item in temp_arr[j][_sage_const_1 ]])

        temp_arr = [None] * (self.m)
        y = [None] * (self.m)
        y_ = [None] * (self.m)

        pool = ThreadPoolExecutor(max_workers=self.m)
        all_task = []
        for i in range(_sage_const_1 , self.m + _sage_const_1 ):
            all_task.append(pool.submit(arr_append, i))

        tp1, tp2 = self.gauss_v(self.sigma_1, self.l + self.k)
        y[_sage_const_0 ] = tp1
        y_[_sage_const_0 ] = vector(self.Rq, [self.Rq(item) for item in tp2])
        wait(all_task, return_when=ALL_COMPLETED)
        pool.shutdown()

        com = []
        for i in range(len(y)):
            com.append(A_ * y_[i])
        off = [t, com]
        st = []
        st.extend(y)
        st.append(com)
        return off, st

    def order(self, mat):
        mat = matrix(mat)
        n_rows = mat.nrows()
        n_cols = mat.ncols()

        mat_copy = [[_sage_const_0  for col in range(n_cols)] for row in range(n_rows)]

        arr = []
        for i in range(n_rows):
            weight = _sage_const_0 
            for j in range(n_cols):
                f = mat[i][j].lift().change_ring(ZZ)
                weight += self.q ** (j * self.N) * f(self.q)
            arr.append((weight, i))
        for i in range(n_rows):
            arr.sort(key=lambda x: x[_sage_const_0 ])
        for i in range(n_rows):
            row = arr[i][_sage_const_1 ]
            mat_copy[i] = mat[row]

        return mat_copy

    # msgs -> off
    def SignOn(self, idx, st, msgs, sk, miu, all_pk, rd):
        def assist1():
            for k in range(self.n):
                W.append(t_array[k])
                W.extend(com_array[k])

        def assist2():
            def assist_sample1():
                b1.extend([self.Samp(hash_res, True)] * (self.m - _sage_const_1 ))
            def assist_sample2():
                b2.extend([self.Samp(hash_res, False)] * (self.m - _sage_const_1 ))

            hash_res = self.Hnon(self.order(list(W)), miu, t_, rd)
            pool_sample = ThreadPoolExecutor(max_workers=_sage_const_4 )
            all_tasks = [pool_sample.submit(assist_sample1), pool_sample.submit(assist_sample2)]
            wait(all_tasks, return_when=ALL_COMPLETED)
            pool_sample.shutdown()

        def assist3():
            for k in range(self.m):
                temp = _sage_const_0 
                for j in range(self.n):
                    temp += com_array[j][k]
                w.append(temp)

        t_array = []
        com_array = []
        for i in range(len(msgs)):
            t_array.append(msgs[i][_sage_const_0 ])
            com_array.append(msgs[i][_sage_const_1 ])
        for i in range(len(t_array)):
            if t_array[i] != all_pk[i] or (t_array[i] == t_array[idx] and i != idx):
                print("[-] fail, pk is error!")
                return None
        t_ = self.KAgg(t_array)

        w = []
        b1 = [self.Rq(_sage_const_1 )]
        b2 = [self.R(_sage_const_1 )]
        W = []

        ppool = ThreadPoolExecutor(max_workers=_sage_const_4 )
        all_task = [ppool.submit(assist1),ppool.submit(assist3)]
        a = self.R(self.Hagg(self.order(t_array), t_array[idx]).lift())
        wait(all_task, return_when=ALL_COMPLETED)
        ppool.shutdown()
        assist2()

        for item in w[-_sage_const_1 ]:
            try:
                item ** (-_sage_const_1 )
            except:
                print("[-] fail, no inverse")
                return None
        w_ = _sage_const_0 
        y_ = _sage_const_0 
        for i in range(self.m):
            w_ += b1[i] * w[i]
            y_ += b2[i] * st[i]
        c = self.R(self.Hsig(w_, miu, t_).lift())
        v = c * a * sk
        z = v + y_

        #if self.RejSamp(v, z, b1) == 0:
        #    print("[-] fail, invalid sample")
        #    return None
        on = (z, w_)

        return on

    def gen_key(self):
        self.A_ = self.Setup()
        pk, sk = [], []
        # Generate pk, sk for all object
        for i in range(self.n):
            pki, ski = self.Gen(self.A_)
            pk.append(pki)
            sk.append(ski)
        return self.A_, pk, sk


    def Offline_assist(self,A_, j, sk, pk):
        offi, sti = self.SignOff(A_, sk[j], pk[j])
        print("[+] Off Siganature {} generate successfully".format(j))
        return offi, sti

    def Offline(self, A_, sk, pk):
        off, st = [], []
        pools = ProcessPoolExecutor(max_workers=self.n)
        all_task = []
        for i in range(self.n):
            all_task.append(pools.submit(self.Offline_assist, A_, i, sk, pk))
        wait(all_task, return_when=ALL_COMPLETED)

        for ele in all_task:
            off.append(ele.result()[_sage_const_0 ])
            st.append(ele.result()[_sage_const_1 ])
        pools.shutdown()
        return off, st

    def Online_assist(self,j,st,off,sk,m,pk):
        temp = self.SignOn(j, st, off, sk, m, pk)
        if not temp:
            print("[-] Siganature {} generate fail".format(j))
            return None
        print("[+] Siganature {} generate successfully".format(j))
        return temp

    def Online(self, st, off, sk, m, pk):
        on = []
        pools = ProcessPoolExecutor(max_workers=self.n)
        all_task = []
        for i in range(self.n):
            all_task.append(pools.submit(self.Online_assist, i, st, off, sk, m, pk))
        wait(all_task, return_when=ALL_COMPLETED)

        for ele in all_task:
            on.append(ele.result())
        pools.shutdown()
        return on

    def verify(self, on, pk, msg):
        # Calulate aggregate signature
        sigma = self.Agg(on)
        # Calculate aggregate public key
        agg_pk = self.KAgg(pk)
        # Verify
        return self.Ver(agg_pk, sigma, msg)

    def signature(self):
        while True:
            off, st = self.Offline(self.A_, self.sk, self.pk)
            on = self.Online(st, off, self.sk, self.message, self.pk)
            if on:
                print("[+] Generate all signature")
                break
        print("Verify signature result: {}".format(self.verify(on, self.pk)))

def auth(pk, sk, system):
    ### finish a challenge ###
    c = system.Rq(sys.Hsig(_sage_const_1 , _sage_const_2 , _sage_const_3 ).lift())
    r = d_gauss(system.Rq, system.N, system.sigma_y)
    y = []
    for _ in range(system.k+system.l):
        y.append(r())
    y = vector(system.Rq, y)
    pk_ = []
    sk_ = []
    for item in pk:
        pk_.append(system.Rq(item))
    for item in sk:
        sk_.append(system.Rq(item))
    pk_ = vector(system.Rq, pk_)
    sk_ = vector(system.Rq, sk_)
    sk_ = c*sk_+y
    t = system.A_*y
    print("debug2", system.A_*y-t)
    return system.A_*sk_ == c*pk_+t


def k2list(f):
    tp = []
    for item in f:
        tp.append(list(item))
    return tp


table = string.ascii_uppercase+string.ascii_lowercase
def random_word():
    return ''.join(random.sample(table, k=_sage_const_5 ))

check_t = '0123456789abcdef'
def check(id):
    tp1 = id[:_sage_const_2 ]
    id = id[_sage_const_2 :]
    if tp1 != '0x':
        return False
    if all([id[i] in check_t for i in range(len(id))]):
        return True
    else:
        return False

def check_sign(item, trc, h):
    all_pk = trc['all_pk']
    msg = item['msg']
    if item['time'] == len(item['sign']):
        if sys.verify(item['sign'], all_pk, msg):
            acc = database.account[trc['source_addr']]
            acc.balance = round(acc.balance - trc['amount'], _sage_const_5 )
            maxl = max(len(usr.address)+_sage_const_29 ,len(str(trc['amount']))+len(trc['target_addr'])+_sage_const_38 )

            out = f"Successful transaction\n"
            out += f"{'#' * (maxl+_sage_const_1 )}\n"
            out += f"# transaction: {usr.address} sent {str(trc['amount'])}".ljust(maxl)+f"#\n"
            out += f"# ETH to {trc['target_addr']} has on the chain ".ljust(maxl)+f"#\n"
            out += f"{'#' * (maxl+_sage_const_1 )}"

            print(out)
            acc.transaction_history.append({"type": "Sent", "amount": "{} ETH to {}".format(trc['amount'], trc['target_addr'])})
            database.transaction_sig.pop(h, None)
            for _ in acc.need:
                try:
                    database.account[_].mulpay.remove(trc)
                except:
                    continue




sys = MusigL(_sage_const_2 )
usr = None
pk = None
sk = None
usr_st = None
word = None
app = Flask(__name__, template_folder='./static/page')
app.config["SECRET_KEY"] = os.urandom(_sage_const_32 ).hex()


@app.route("/")
def index():
    try:
        f = open('account.bin', 'rb')
        f.close()
        return redirect(url_for('login'))
    except:
        return redirect(url_for('welcome'))


@app.route("/welcome")
def welcome():
    return render_template('new.html')


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('NewWallet.html')
    global word
    word = [random_word() for _ in range(_sage_const_12 )]
    pwd = request.form.get("password")
    pk, sk = sys.Gen(int(sha256(' '.join(word).encode()).hexdigest(), _sage_const_16 ))
    off, st = sys.SignOff(sys.A_, pk)
    st1 = []
    for item in st[:-_sage_const_1 ]:
        st1.append(k2list(item))
    st2 = []
    for item in st[-_sage_const_1 ]:
        st2.append(k2list(item))
    enc_st = local_enc.enc_key(str(st1)+"+"+str(st2), str(k2list(sk)))
    address = '0x'+hashlib.shake_128(str(k2list(pk)).encode()).hexdigest(int(_sage_const_10 ))
    obj = database.User(address, (off, enc_st), pk)
    database.account[address] = obj
    f = open("account.bin", mode='a')
    f.close()
    f = open("account.bin", 'wb')
    f.write(base64.b64encode(local_enc.enc_key(str(k2list(pk))+"+"+str(k2list(sk)), pwd)))
    f.close()
    return redirect(url_for('show'))


@app.route("/show")
def show():
    return render_template('NewWallet2.html', wd=word)


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    password = request.form.get("pwd")
    enc_account = base64.b64decode(open('account.bin', 'rb').read())
    try:
        account = local_enc.dec_key(enc_account, password).decode().split('+')
        pk_, sk_ = account
        address = '0x'+hashlib.shake_128(pk_.encode()).hexdigest(int(_sage_const_10 ))
        global pk, sk
        pk = eval(pk_)
        sk = eval(sk_)
        if auth(pk, sk, sys):
            global usr
            usr = database.account[address]
            print("#################################################")
            print(f'# user {usr.address} login successful  #')
            print("#################################################")
            st1, st2 = local_enc.dec_key(usr.prec[_sage_const_1 ], str(sk)).decode().split('+')
            st1 = eval(st1)
            st2 = eval(st2)
            global usr_st
            usr_st = []
            for item in st1:
                st1_ = []
                for pl in item:
                    st1_.append(sys.R(pl))
                usr_st.append(vector(sys.R, st1_))
            tp = []
            for item in st2:
                st2_ = []
                for pl in item:
                    st2_.append(sys.Rq(pl))
                tp.append(vector(sys.Rq, st2_))
            usr_st.append(tp)
            return redirect(url_for('usr_state'))
        else:
            return render_template('login.html', mes="Incorrect password")
    except Exception as e:
        print(str(e))
        return render_template('login.html', mes="Incorrect password")


@app.route("/pay", methods=['POST', 'GET'])
def pay_state():
    if request.method == 'GET':
        return render_template('prev_pay.html')
    data = request.get_data()
    data_dict = {}
    for item in data.decode().split('&'):
        key, value = item.split('=')
        data_dict[key] = value
    total_amount = float(data_dict['totalAmount'])
    address = data_dict['address']
    global usr
    if usr.balance >= total_amount:
        if len(usr.need):
            off = [database.account[item].prec[_sage_const_0 ] for item in usr.need]
            st = usr_st
            all_pk = [database.account[item].pk for item in usr.need]
            trc = {"source_addr": usr.address, "target_addr": address, "amount": total_amount,                "token": sha256(str(time.time()).encode()).hexdigest(), "off": off, "all_pk": all_pk}
            h = sm3_hash(bytes_to_list(str(trc).encode()))
            database.transaction_sig[h] = {"time": len(usr.need), "sign": [], "msg": "aaaa"}
            for item in usr.need:
                database.account[item].mulpay.append(trc)
            return redirect('usr_state')
        else:
            usr.balance = round(usr.balance - total_amount, _sage_const_5 )
            usr.transaction_history.append({"type": "Sent", "amount": "{} ETH to {}".format(total_amount, address)})
            maxl = max(len(usr.address)+_sage_const_29 ,len(str(total_amount))+len(address)+_sage_const_38 )

            out = f"Successful transaction\n"
            out += f"{'#' * (maxl+_sage_const_1 )}\n"
            out += f"# transaction: {usr.address} sent {str(total_amount)}".ljust(maxl)+f"#\n"
            out += f"# ETH to {address} has on the chain ".ljust(maxl)+f"#\n"
            out += f"{'#' * (maxl+_sage_const_1 )}"

            print(out)
            return redirect('usr_state')
    else:
        return redirect('login')


@app.route("/usr_state", methods=['POST', 'GET'])
def usr_state():
    global usr
    if request.method == 'GET':
        maxl = max(len(usr.address), len(str(usr.balance)))
        us = f'user state:\n'
        us += f'{"#"*(maxl+_sage_const_14 )}\n'
        us += f'# address: {usr.address.ljust(maxl)}  #\n'
        us += f'# balance: ${str(usr.balance).ljust(maxl)} #\n'
        us += f'{"#"*(maxl+_sage_const_14 )}\n'
        print(us)
        print("Waiting transaction info: ")
        print(database.transaction_sig)
        return render_template('user.html', address=usr.address, balance=usr.balance,                               transaction_history=usr.transaction_history, friend_list=usr.need, p_list = usr.mulpay)
    return render_template('user.html', address=usr.address, balance=usr.balance,                           transaction_history=usr.transaction_history, friend_list=usr.need, p_list = usr.mulpay)


@app.route("/forget", methods=['POST', 'GET'])
def forget():
    if request.method == 'GET':
        return render_template('forget.html')
    password = request.form.get("pwd1")
    com_password = request.form.get("pwd2")
    wd = request.form.get("word")
    try:
        assert password == com_password
        global word
        word = wd.split(' ')
        pk, sk = sys.Gen(int(sha256(' '.join(word).encode()).hexdigest(), _sage_const_16 ))
        f = open("account.bin", mode='a')
        f.close()
        f = open("account.bin", 'wb')
        f.write(base64.b64encode(local_enc.enc_key(str(k2list(pk)) + "+" + str(k2list(sk)), password)))
        f.close()
        return redirect(url_for('login'))
    except:
        return render_template('forget.html', mes="Password confirmation does not match")


@app.route('/add_friend', methods=['POST', 'GET'])
def add_friend():
    friend_id = request.form['friend_id']
    if friend_id not in usr.need and check(friend_id):
        usr.need.append(friend_id)
    return redirect('usr_state')


@app.route('/delete_friend', methods=['POST', 'GET'])
def delete_friend():
    friend_id = request.form['friend_id']
    if friend_id in usr.need and check(friend_id):
        usr.need.remove(friend_id)
    return redirect('usr_state')


@app.route('/mulsign', methods=['POST', 'GET'])
def mulsign():
    token = request.form['token']
    for item in usr.mulpay:
        if item['token'] == token:
            global sk
            sk_ = []
            for pl in sk:
                sk_.append(sys.R(pl))
            sk_ = vector(sys.R, sk_)
            off = item['off']
            st = usr_st
            all_pk = item['all_pk']
            h = sm3_hash(bytes_to_list(str(item).encode()))
            msg = database.transaction_sig[h]['msg']
            on = sys.SignOn(off.index(usr.prec[_sage_const_0 ]), st, off, sk_, msg, all_pk, _sage_const_0 )
            payment = database.transaction_sig[h]
            payment['sign'].append(on)
            check_sign(payment, item, h)
    return redirect('usr_state')

app.run()


