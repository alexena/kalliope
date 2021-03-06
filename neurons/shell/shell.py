import logging
import subprocess
import threading
from core.NeuronModule import NeuronModule, MissingParameterException

logging.basicConfig()
logger = logging.getLogger("kalliope")


class AsyncShell(threading.Thread):
    def __init__(self, cmd):
        self.stdout = None
        self.stderr = None
        self.cmd = cmd
        threading.Thread.__init__(self)

    def run(self):
        p = subprocess.Popen(self.cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        self.stdout, self.stderr = p.communicate()


class Shell(NeuronModule):
    def __init__(self, **kwargs):
        super(Shell, self).__init__(**kwargs)

        # get the command
        cmd = kwargs.get('cmd', None)
        # get if the user select a blocking command or not
        async = kwargs.get('async', False)

        if cmd is None:
            raise MissingParameterException("cmd parameter required")

        # run the command
        if not async:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            message = {
                "output": output,
                "returncode": p.returncode
            }
            self.say(message)

        else:
            async_shell = AsyncShell(cmd=cmd)
            async_shell.start()




