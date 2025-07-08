import sys
import os
import subprocess


def check_java_version():
    try:
        retcode = subprocess.call(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if retcode < 0:
            print("Java not in Path", -retcode, file=sys.stderr)
        else:
            print("Java version check successful.")
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
        sys.exit(1)


def main():
    check_java_version()

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    appdir = os.path.dirname(os.path.dirname(__file__))

    if not appdir:
        appdir = os.getcwd()
    else:
        print("App directory:", appdir)

    c1 = os.path.join(appdir, "bin", "apache-flume-1.3.1-bin", "lib", "*")
    c2 = os.path.join(appdir, "bin", "apache-flume-1.3.1-bin", "lib", "flume-ng-node-1.3.1.jar")
    c3 = os.path.join(appdir, "bin", "dtFlume.jar")

    classpath = os.pathsep.join([c1, c2, c3])
    print("Class path:", classpath)

    log4j = os.path.join(appdir, "bin", "apache-flume-1.3.1-bin", "conf", "log4j.properties")
    flumeconf = os.path.join(appdir, "bin", "flume-conf.properties")
    pidfilename = os.path.join(appdir, 'flume.pid')

    currentOS = os.name

    if currentOS == 'posix':
        if os.path.exists(pidfilename):
            with open(pidfilename, 'r') as f:
                pid = int(f.read().strip())
            if os.path.exists(f"/proc/{pid}"):
                print(f"Process already running as PID {pid}", file=sys.stderr)
                sys.exit(1)
            else:
                print("PID file exists but process is no longer running. Removing pidfile", file=sys.stderr)
                os.remove(pidfilename)
    elif currentOS == 'nt':
        if os.path.exists(pidfilename):
            with open(pidfilename, 'r') as f:
                pid = int(f.read().strip())
            try:
                tasklist = subprocess.check_output(f'tasklist /fi "PID eq {pid}"', stderr=subprocess.PIPE).strip().decode()
                if "INFO" not in tasklist:
                    print("Flume or process with same PID already running", file=sys.stderr)
                    sys.exit(1)
            except subprocess.CalledProcessError:
                pass # Process not found
    else:
        print("Unsupported OS", file=sys.stderr)
        sys.exit(1)

    cmd = [
        'java',
        '-Xmx20m',
        f'-Dlog4j.configuration=file:{log4j}',
        '-cp',
        classpath,
        'org.apache.flume.node.Application',
        '-f',
        flumeconf,
        '-n',
        'agent1'
    ]

    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with open(pidfilename, 'w') as f:
            f.write(str(p.pid))

        stdout, stderr = p.communicate()
        retcode = p.wait()

        if stdout:
            print(stdout.decode())
        if stderr:
            print(stderr.decode(), file=sys.stderr)

        if retcode < 0:
            print("Child was terminated by signal", -retcode, file=sys.stderr)
        else:
            print("Child returned", retcode)

    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
    except Exception as e:
        print("An unexpected error occurred:", e, file=sys.stderr)


if __name__ == "__main__":
    main()

		



