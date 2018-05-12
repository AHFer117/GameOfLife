#!/usr/bin/env python
#  -*- coding: utf-8 -*
"""
Game of Life
Any live cell with fewer than two live neighbours dies, as if caused by underpopulation.
Any live cell with two or three live neighbours lives on to the next generation.
Any live cell with more than three live neighbours dies, as if by overpopulation.Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
"""
import sys
import numpy as np


def seed(w, h):    r = np.random.randint(0, 10, (w + 2, h)) < 3


r[0, :] = 0
r[-1, :] = 0
return r
 
 
def display(data, w, h, sleep=False):    for j in range(h):        for i in range(1, w + 1):            if data[i, j]:                sys.stdout.write('#')            else:                sys.stdout.write(' ')        sys.stdout.write('\n')    sys.stdout.write('\n------------------------------------------\n')    sys.stdout.flush()    if sleep:        import time        time.sleep(0.1)
 
 
def run(data, w, h):    """Runs a single tick in the game of life"""    old_data = data.copy()    for i in range(1, w+1):        for j in range(h):            # count number of neighbors            n = 0            if old_data[i-1, j]:                n += 1            if old_data[i+1, j]:                n += 1            if j > 0:                if old_data[i, j-1]:                    n += 1                if old_data[i-1, j-1]:                    n += 1                if old_data[i+1, j-1]:                    n += 1            elif j == 0:                # connect top to bottom                if old_data[i, -1]:                    n += 1                if old_data[i-1, -1]:                    n += 1                if old_data[i+1, -1]:                    n += 1            if j < h-1:                if old_data[i, j+1]:                    n += 1                if old_data[i-1, j+1]:                    n += 1                if old_data[i+1, j+1]:                    n += 1            elif j == h-1:                # connect bottom to top                if old_data[i, 0]:                    n += 1                if old_data[i-1, 0]:                    n += 1                if old_data[i+1, 0]:                    n += 1
             # apply game of life rules based on number of neighbors            if old_data[i, j]:                if n < 2 or n > 3:                    data[i, j] = False            elif n == 3:                data[i, j] = True
 
 
def chunk(data, n, w, h):    result = []    c = 0    for i in range(n):        cw = int(w / n) + 2        if i == n-1:            cw += w % n        ch = h        r = np.empty((cw, ch), dtype=np.bool_)        for k in range(cw):            r[k] = data[k+c]        result.append(r)        c += int(w / n)    return result
 
 
def unchunk(data, n, w, h):    result = np.zeros((w+2, h), dtype=np.bool_)    c = 1    for chnk in data:        for k in range(1, chnk.shape[0] - 1):            result[c] = chnk[k]            c += 1    return result
 
 
def gameoflife_mpi(w=40, h=40, maxticks=-1, show=True):    from mpi4py import MPI    comm = MPI.COMM_WORLD    size = comm.Get_size()    rank = comm.Get_rank()
     # initialize data randomly    data = seed(w, h)    tick = 0    while tick != maxticks:        chunks = None        if rank == 0:            # main node            if show:                display(data, w, h)            # divide data into chunks            chunks = chunk(data, size, w, h)
         # send chunks to nodes if we're node 0, else receive that data        data = comm.scatter(chunks, root=0)
         # run one tick of the game of life        run(data, data.shape[0] - 2, data.shape[1])
         # gather data from all the nodes if we're node 0, else send our data        data = comm.gather(data, root=0)        if rank == 0:            # on node zero            data = unchunk(data, size, w, h)        tick += 1
 
 
if __name__ == '__main__':    try:        show = False        args = list(sys.argv)        if len(args) >= 2 and args[1] == '-v':            show = True            del args[1]        if len(args) == 1:            gameoflife_mpi(show=show)        if len(args) == 3:            gameoflife_mpi(int(args[1]), int(args[2]), show=show)        else:            gameoflife_mpi(int(args[1]), int(args[2]), int(args[3]), show=show)    except:        print("Usage:\n\tpython gameoflife.py [-v] [<width> <height> [maxticks]]")
