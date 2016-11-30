import os
import sys
import tempfile

import vmprof
from vmprof.upload import upload as upload_vmprofile
from jitlog.parser import parse_jitlog

try:
    import _jitlog
except ImportError:
    _jitlog = None


OUTPUT_CLI = 'cli'
OUTPUT_WEB = 'web'
OUTPUT_FILE = 'file'


def upload_stats(stats, forest, web_url, web_auth):
    name = ""  # No name because vmprof is run in wsgi application.
    argv = ""  # No arguments because vmprof is run by middleware. (It's not CLI!)
    host = web_url
    auth = web_auth
    sys.stderr.write("Compiling and uploading to {}...\n".format(web_url))
    upload_vmprofile(stats, name, argv, host, auth, forest)


def show_stats(filename, output_mode, web_url, web_auth):
    if output_mode == OUTPUT_FILE:
        return

    stats = vmprof.read_profile(filename)
    forest = None

    if output_mode == OUTPUT_CLI:
        vmprof.cli.show(stats)
    elif output_mode == OUTPUT_WEB:
        upload_stats(stats, forest, web_url, web_auth)


class VmprofMiddleware:
    def __init__(self, app,
                 period=0.001,
                 web_url='http://vmprof.com', web_auth=None, mem=False, lines=False, jitlog=False,
                 web=None, output=None):
        """
        Parameter details are here:
            https://github.com/vmprof/vmprof-python/blob/master/vmprof/cli.py#L7-L72

        :param app: Your WSGI application object.
        :param float period: Sampling period (in microseconds)
        :param str web_auth: Authtoken for your acount on the server, works only when --web is used
        :param str web_url: Provide URL instead of the default vmprof.com)
        :param bool mem: Do memory profiling as well
        :param bool lines: Store lines execution stats
        :param bool jitlog: Upload the jitlog to remote server (defaults to vmprof.com)
        :param bool web: Upload profiling stats to a remote server (defaults to vmprof.com)
        :param output: Save profiling data to file
        """
        self.app = app
        self.web_url = web_url
        self.web_auth = web_auth
        self.period = period
        self.mem = mem
        self.lines = lines

        if web:
            self.output_mode = OUTPUT_WEB
        elif output:
            self.output_mode = OUTPUT_FILE
        else:
            self.output_mode = OUTPUT_CLI

        if self.output_mode == OUTPUT_FILE:
            self.prof_name = output
            self.prof_file = open(self.prof_name, 'w+b')
        else:
            self.prof_file = tempfile.NamedTemporaryFile(delete=False)
            self.prof_name = self.prof_file.name

        if jitlog and _jitlog:
            fd = os.open(self.prof_file + '.jitlog',
                         os.O_WRONLY | os.O_TRUNC | os.O_CREAT)
            _jitlog.enable(fd)

    def start(self):
        vmprof.enable(self.prof_file.fileno(), self.period, self.mem, self.lines)

    def stop(self):
        vmprof.disable()
        self.prof_file.close()
        show_stats(self.prof_name, self.output_mode, web_url=self.web_url, web_auth=self.web_auth)
        if self.output_mode != OUTPUT_FILE:
            os.unlink(self.prof_name)

    def __call__(self, *args, **kwargs):
        return self.app(*args, **kwargs)
