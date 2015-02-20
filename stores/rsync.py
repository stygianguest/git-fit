from os.path import exists, join as joinpath, dirname
import os
from subprocess import Popen as popen, PIPE
from fitlib import fitDir, DataStore

class Store(DataStore):

    def __init__(self, *args, **kwds):
        location = popen('git config fit.datastore.location'.split(), stdout=PIPE).communicate()[0].strip()
        self.dir = location or joinpath(fitDir, 'store')

    def get(self, key, dst, size):
        return popen(['rsync', '--size-only', key, dst]).wait() == 0

    def put(self, src, dst, size):
        if exists(src):
            return popen(['rsync', '-R', src, self.dir]).wait() == 0

    def check(self, key):
        path = joinpath(self.dir, key)

        if popen(['rsync', '-q', '--list-only', path], stderr=devnull, stdout=devnull).wait() == 0 :
            return path
