#!/usr/bin/env python

import sys, os, time, atexit
from signal import SIGTERM

class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, working_dir, uid=None, gid=None, stdin=None, stdout=None, stderr=None):
        self.pidfile = pidfile
        self.working_dir = working_dir
        self.uid = uid
        self.gid = gid
        self.stdin = stdin or os.devnull
        self.stdout = stdout or os.devnull
        self.stderr = stderr or os.devnull

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork() #@UndefinedVariable
            if pid > 0:
                # return from first parent to continue execution
                return True
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.setsid() #@UndefinedVariable
        os.umask(0)

        # do second fork
        try:
            pid = os.fork() #@UndefinedVariable
            if pid > 0:
                # exit second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()

        if self.working_dir is not None:
            os.chdir(self.working_dir)
        if self.uid is not None:
            os.seteuid(self.uid) #@UndefinedVariable
        if self.gid is not None:
            os.setegid(self.gid) #@UndefinedVariable

        self.mask_standard_file_descriptors()
        # write pidfile
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)
        # register the function to delete pidfile at process exit
        atexit.register(self.delpid)

        return False # return False means we are in the "daemonized" child process

    def delpid(self):
        os.remove(self.pidfile)

    def mask_standard_file_descriptors(self):
        self.init_stdin = os.dup(sys.stdin.fileno())
        self.init_stdout = os.dup(sys.stdout.fileno())
        self.init_stderr = os.dup(sys.stderr.fileno())
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def unmask_standard_file_descriptors(self):
        os.dup2(self.init_stdin, sys.stdin.fileno())
        os.dup2(self.init_stdout, sys.stdout.fileno())
        os.dup2(self.init_stderr, sys.stderr.fileno())

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            try:
                os.kill(pid, 0)
                message = "Daemon already running.\n"
                sys.stderr.write(message % self.pidfile)
                sys.exit(1)
            except OSError:
                # process with PID=pid does not exist, 
                # we delete the PID file and continue
                message = "Process %d is not running. Deleting pidfile %s...\n"
                sys.stderr.write(message % (pid, self.pidfile))
                os.remove(self.pidfile)

        parent = self.daemonize()
        if parent:
            return
        try:
            # we can only be here if we are in the daemonized process
            self.run()
        except:
            self.unmask_standard_file_descriptors()
            raise
        # make sure we exit here otherwise strange things could happen :cuir:
        sys.exit(0)

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM) #@UndefinedVariable
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called
        after the process has been daemonized by start() or restart().
        """
        pass
