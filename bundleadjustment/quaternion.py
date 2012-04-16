#!/usr/bin/python
#coding:utf-8

# Copyright 2012 Nicolau Leal Werneck, Anna Helena Reali Costa and
# Universidade de São Paulo
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np

def random_quaternion(angle = 1.0):
    Q = Quat(np.random.rand(4))
    ## Get a new trial until we are satisfied with the norm (inside an
    ## spherical shell).
    while Q.norm() > 1.0 or Q.norm() < 0.1:
        Q = Quat(np.random.rand(4))
    nQ = angle * Q.q[1:]
    return Quat(nQ).normalize()

class Quat:
    def __init__(self, a, b=None,c=None,d=None):
        if b==None and type(a) == type(np.array([3.1415])):
            if a.shape[0] == 4:
                self.q = np.copy(a)
            elif a.shape[0] == 3:
                self.q = np.r_[np.sqrt(1-(a**2).sum()), a]

        elif a!=None and b!=None and c!=None and d!=None:
            self.q = np.array([a,b,c,d])
        elif a!=None and b!=None and c!=None and d==None:
            self.q = np.r_[np.sqrt(1.0-(a**2+b**2+c**2)), a,b,c]
        else:
            raise TypeError

    def __repr__(self):
        return 'Quat(%f, %f, %f, %f)'%tuple(self.q)

    def inverse(self):
        return Quat(self.q * np.array([1,-1,-1,-1]))

    def rot(self):
        a,b,c,d = self.q
        return np.array([ [(a*a+b*b-c*c-d*d), (2*b*c-2*a*d),     (2*b*d+2*a*c)     ],
                          [(2*b*c+2*a*d),     (a*a-b*b+c*c-d*d), (2*c*d-2*a*b)     ],
                          [(2*b*d-2*a*c),     (2*c*d+2*a*b),     (a*a-b*b-c*c+d*d)] ] )

    def norm(self):
        return np.sqrt((self.q**2).sum())
    def normalize(self):
        self.q = self.q / self.norm()
        if self.q[0]<0:
            self.q = self.q * -1
        return self

    def __mul__(self,bb):
        a,b = self.q, bb.q 
        return Quat(
            a[0]*b[0] - a[1]*b[1] - a[2]*b[2]-a[3]*b[3],
            a[0]*b[1] + a[1]*b[0] - a[2]*b[3]+a[3]*b[2],
            a[0]*b[2] + a[1]*b[3] + a[2]*b[0]-a[3]*b[1],
            a[0]*b[3] - a[1]*b[2] + a[2]*b[1]+a[3]*b[0] )

    def __div__(self,bb):
        a,b = self.q, bb.q 
        return Quat(
            a[0]*b[0] + a[1]*b[1] + a[2]*b[2]+a[3]*b[3],
           -a[0]*b[1] + a[1]*b[0] + a[2]*b[3]-a[3]*b[2],
           -a[0]*b[2] - a[1]*b[3] + a[2]*b[0]+a[3]*b[1],
           -a[0]*b[3] + a[1]*b[2] - a[2]*b[1]+a[3]*b[0] )

    def __add__(self,bb):
        a,b = self.q, bb.q 
        return Quat(a[0]+b[0],a[1]+b[1],a[2]+b[2],a[3]+b[3])
    
    def __sub__(self,bb):
        a,b = self.q, bb.q 
        return Quat(a[0]-b[0],a[1]-b[1],a[2]-b[2],a[3]-b[3])

    def angle(self):
        return np.arcsin(np.sqrt((self.q[1:]**2).sum()))*2*180/np.pi

    def sqrt(self):
        f = np.sqrt((self.q[1:]**2).sum())
        if f == 0:
            return Quat(1,0,0,0)
        ang = np.arcsin(f)*2
        newang = ang / 2.0
        newf = np.sin(newang / 2)
        return Quat(self.q[1:] * newf / f)

    def fraction(self, factor):
        f = np.sqrt((self.q[1:]**2).sum())
        ang = np.arcsin(f)*2
        newang = ang / factor
        newf = np.sin(newang / 2)
        return Quat(self.q[1:] * newf/f)

    def canonical(self):
        ## From the Deutscher 2002 article
        absq = np.abs(self.q)
        ii = np.argsort(absq)[-1::-1]
        p,q,r,s = np.sort(absq)[-1::-1]
        v1,v2,v3 = p, (p+q)/np.sqrt(2.), (p+q+r+s)/2.

        r = np.array([0.,0,0,0])

        if v1 >= v2 and v1>=v3:
            r[ii[0]] = np.sign(self.q[ii[0]])
        elif v2 > v1 and v2>=v3:
            r[ii[0]] = np.sign(self.q[ii[0]])
            r[ii[1]] = np.sign(self.q[ii[1]])
        else:
            r = np.sign(self.q)
        r=Quat(r)
        r.normalize()
        return r.inverse() * self


if __name__ == '__main__':

    for n in range(20):
        q = Quat(np.random.rand(4)*2-1)
        r = Quat(q.q)
        q.normalize()
        print q
        print q.canonical()
        print r
        print r*q
        print
