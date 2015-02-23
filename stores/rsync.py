import os.path# import , join as joinpath
import posixpath
import tempfile

from subprocess import Popen as popen, PIPE
from fitlib import DataStore

SHOW_PROGRESS_LIMIT = 1e+7 # show progress of transfer for files larger than this

class Store(DataStore):

    def __init__(self, *args, **kwds):
        self.location = popen('git config fit.datastore.location'.split(), stdout=PIPE).communicate()[0].strip()
        if not self.location :
            raise Exception("error: No datastore location given, please specify fit.datastore.location in git config.")

        self.dir = tempfile.mkdtemp()

    def __del__(self) :
        if popen(["rm",  "-r", self.dir]).wait() != 0 :
            print "Failed to remove temporary folder %s" % self.dir

    def get(self, key, dst, size):
        #print "get(%s, %s)" % (key, dst)

        reporting = "--progress" if size > SHOW_PROGRESS_LIMIT else "--quiet"

        return popen(['rsync', reporting, key, dst]).wait() == 0

    def put(self, src, dst, size):
        #print "put(%s, %s)" % (src, dst)

        # copy the file in the temporary directory and execute rsync there
        # this way, we can create the necessary directories using rsync -R
        tmpfile = os.path.join(self.dir, dst)

        reporting = "--progress" if size > SHOW_PROGRESS_LIMIT else "--quiet"

        return (
            popen(['mkdir', '-p', os.path.dirname(tmpfile)]).wait() == 0
        and popen(['cp', src, tmpfile]).wait() == 0
        and popen(['rsync', reporting, '--relative', dst, self.location], cwd=self.dir).wait() == 0
        )

    def check(self, key):
        path = posixpath.join(self.location, key)

        # rsync -q isn't quiet when the file doesn't exist
        # therefore we pipe to /dev/null
        with file(os.devnull, 'w') as devnull :
            if popen(['rsync', '--list-only', path], stderr=devnull, stdout=devnull).wait() == 0 :
                return path
