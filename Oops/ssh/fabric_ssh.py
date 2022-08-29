from fabric import Connection

from Oops.libs.commonfun import conv_client
from config import config_env
import pathlib


def disk_free(c):
    uname = c.run('uname -s', hide=True)
    if 'Linux' in uname.stdout:
        command = "df -h / | tail -n1 | awk '{print $5}'"
        return c.run(command, hide=True).stdout.strip()
    err = "No idea how to get disk space on {}!".format(uname)
    raise SystemExit(err)


username = config_env['SSH_USER'] if 'SSH_USER' in config_env else 'root'
password = config_env['SSH_PASS'] if 'SSH_PASS' in config_env else '123456'
hosts = config_env['HOSTS'] if 'HOSTS' in config_env else 'localhost'
key_filename = config_env['SSH_CERT'] if 'SSH_CERT' in config_env else 'None'
hosts = conv_client(hosts)

connect_kwargs = {'password': password}
if key_filename != 'None':
    p = pathlib.PosixPath(key_filename)
    key_filename = str(p.expanduser())
    connect_kwargs = dict(key_filename=key_filename)

for host in hosts:
    c = Connection(host=host, user=username,
                   connect_kwargs=connect_kwargs)

    result = c.run('sudo uname -s', hide=True)
    msg = "Ran {0.command!r} on {0.connection.host}, got stdout:\n{0.stdout}"
    print(msg.format(result))
    print(f"{host} Disk Usage: /# \n" + disk_free(c))
    result = c.sudo(f"sudo ls /root", shell=False)
    print(msg.format(result))


