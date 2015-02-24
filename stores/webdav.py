import easywebdav
import posixpath
from subprocess import Popen as popen, PIPE

import fitlib

class Store(fitlib.DataStore):

    def __init__(self, *args, **kwds):
        self.location = popen('git config fit.datastore.location'.split(), stdout=PIPE).communicate()[0].strip()
        self.port = int(popen('git config fit.datastore.port'.split(), stdout=PIPE).communicate()[0].strip())

        self._connection = None

    @property
    def connection(self) :
        import easywebdav

        if not self._connection :
            self.connection = easywebdav.connect(
                self.location,
                port=self.port,
            )

        return self.connection

    def get(self, src, dst, size):
        try :
            self.connection.download(src, dst)
        except e:
            print e
            raise

        return True

    def put(self, src, dst, size):
        dstpath = posixpath.dirname(dst)

        if not self.connection.exists(dstpath) :
            self.connection.mkdirs(dstpath)

        self.connection.upload(src, dst)

        return True

    def check(self, key):
        if self.connection.exists(key) :
            return key

