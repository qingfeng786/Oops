import pathlib
import sys
from multiprocessing import Pool

import click
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.ssh_exception import AuthenticationException
from scp import SCPClient, SCPException

from Oops.libs.commonfun import conv_client, checkdns
from config import config_env
import logging

logger = logging.getLogger("ssh")


class Client:
    def __init__(self, server, username='None', password='None', ssh_cert=None):
        """
        init Client to run some cmds in server.
        :param server:
        :param username:
        :param password:
        :param ssh_cert:
        """
        self.remote_url = server
        self.remote_user = username
        self.remote_ssh_key = ssh_cert
        self.pkey = self.__get_ssh_key()
        self.sshUser = username
        self.password = password
        self.client = None

    def __get_ssh_key(self):
        """Get our SSh key."""
        try:
            pkey = RSAKey.from_private_key_file(self.remote_ssh_key)
        except:
            pkey = None
        return pkey

    def __connect(self):
        """Connect to remote."""
        client = None
        if self.client is None:
            try:
                client = SSHClient()
                client.load_system_host_keys()
                client.set_missing_host_key_policy(AutoAddPolicy())
                client.connect(self.remote_url,
                               username=self.sshUser,
                               password=self.password)
            except AuthenticationException:
                if self.pkey is None:
                    raise AuthenticationException(f"Please check ssh user/password.")
                else:
                    logger.warning(f"User/pass logged server ({self.remote_url}) failed, will try ssh cert.")
        else:
            client = None
        try:
            if self.pkey and client is None:
                client = SSHClient()
                client.load_system_host_keys()
                client.set_missing_host_key_policy(AutoAddPolicy())
                client.connect(self.remote_url,
                               username=self.remote_user,
                               pkey=self.pkey)
        except AuthenticationException:
            raise AuthenticationException('Authentication failed: did you remember to create an SSH key?')

        finally:
            return client

    def upload(self, file, remote_directory):
        """Upload a single file to a remote directory"""
        if self.client is None:
            self.client = self.__connect()
        scp = SCPClient(self.client.get_transport())
        try:
            scp.put(file,
                    recursive=True,
                    remote_path=remote_directory)
        except SCPException:
            raise SCPException.message
        finally:
            scp.close()

    def execute(self, cmd):
        """Executes a single unix command."""
        if self.client is None:
            self.client = self.__connect()
        stdin, stdout, stderr = self.client.exec_command(cmd)
        stderr = list(stderr)
        stdout = list(stdout)
        if stderr:
            log = stderr
        else:
            log = stdout
        rs = {'host': self.remote_url, 'log': log}
        if stderr:
            rs['msg'] = 'Ran cmd failed.'
        return rs

    def disconnect(self):
        """Close ssh connection."""
        self.client.close()

    def redhat_release(self):
        """Executes a single unix command."""
        if self.client is None:
            self.client = self.__connect()
        if self.client is None:
            raise Exception(f"ssh connect issue, please check.")
        stdin, stdout, stderr = self.client.exec_command('sudo cat /etc/redhat-release')
        readlines = stdout.readlines()
        readlines = [str(i).strip() for i in readlines]
        if len(readlines) == 1:
            svrtype = readlines[0]
        else:
            svrtype = None
        return svrtype


def runcmd(kwargs):
    try:
        host = kwargs[0]
        cmd = kwargs[1]
        username = config_env['SSH_USER'] if 'SSH_USER' in config_env else 'root'
        password = config_env['SSH_PASS'] if 'SSH_PASS' in config_env else 'password'
        key_filename = config_env['SSH_CERT'] if 'SSH_CERT' in config_env else 'None'
        p = pathlib.PosixPath(key_filename)
        key_filename = str(p.expanduser())
        cl = Client(host, username=username, password=password, ssh_cert=key_filename)
        rs = cl.execute(cmd)
        cl.disconnect()
        return rs
    except:
        return None


@click.command()
@click.option('-h', default='xxxx.example.com', help='hostname.')
@click.option('-cmd', default='command', help='command.')
def main(h, cmd):
    POOL_SIZE = 4
    hosts = conv_client(h)
    hostsip = [i for i in hosts if checkdns(i)]
    print(hostsip)
    if not hostsip:
        print('Warning no hosts exists, please check hostnames.')
        sys.exit(1)
    qjoblist = [(i, cmd) for i in hostsip]
    with Pool(POOL_SIZE) as pool:
        results = pool.map(runcmd, qjoblist)
    for i in results:
        if i.get('host'):
            print(i['host'] + ' #')
            for m in i['log']:
                print(m, end='')


if __name__ == '__main__':
    main()
