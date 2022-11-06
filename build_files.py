import subprocess as sp
import os

# https://github.com/stevenbell/vhdlweb/blob/master/vhdlweb_build.py
def safe_run(command, cwd, timeout=3, **kwargs):
  with sp.Popen(command, stdout=sp.PIPE, stderr=sp.STDOUT, preexec_fn=os.setsid,cwd=cwd, **kwargs) as process:
    try:
      output = process.communicate(timeout=timeout)[0]
      return(output)
    except sp.CalledProcessError as e:
        if e.returncode == -sp.signal.SIGSEGV:
            return(b"Program segfaulted")
    except sp.TimeoutExpired:
      os.killpg(process.pid, sp.signal.SIGINT)
      output = process.communicate()[0]
      return("Program timed out after {} seconds. Output up to this point was:\n\n"\
             .format(timeout).encode('utf-8') + output[0:5000])
