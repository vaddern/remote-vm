import subprocess


def shell(cmd, out=""):
    try:
        if (not out):
            return subprocess.check_call(cmd, shell=True)
        else:
            with open(out, 'w') as f:
                return subprocess.check_call(cmd, shell=True, stdout=f, stderr=f)
    except subprocess.CalledProcessError as e:
        print(str(e))
        return e.returncode
