import re
import socket
import logging
import dns.resolver as dns

logger = logging.getLogger("commonfun")
from config import configenv


def checkdns(hostname: str, multi_ip: bool=False):
    """
    This for check fqdn if have ip,
    if have dns record, will return ip  or return False.
    :param hostname:
    :param multi_ip:
    :return:
    """
    ip = re.compile(
        '(([2][5][0-5]\.)|([2][0-4][0-9]\.)|([0-1]?[0-9]?[0-9]\.)){3}' +
        '(([2][5][0-5])|([2][0-4][0-9])|([0-1]?[0-9]?[0-9]))')
    if ip.search(hostname):
        return {'status': 'SUCCESS', 'ip': hostname}

    try:
        answers = dns.query(hostname, 'A')
        iplist = [i.address for i in answers]
        if len(iplist) == 1:
            return {'status': 'SUCCESS', 'ip': iplist[0]}
        else:
            logger.error(f"This {hostname} have over 1 IP: {iplist}.")
            if multi_ip:
                return {'status': 'SUCCESS', 'ip': iplist}
            return {'status': 'SUCCESS', 'ip': iplist[0]}
    except Exception:
        return False


def is_valid_ipv4_address(address: str):
    """
    check the address if ipv4 address
    :param address:
    :return:
    """
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False
    return True


def conv_client(clients: str, op='general',
                default_domain=None):
    """_summary_

    Args:
        clients (str): like strongtest0[01:100] or 192.168.1.1[00:30]
        op (str, optional): _description_. Defaults to 'general'.
        default_domain (str, optional): when clients is shut name, will
        auto add default domain. Defaults to 'example.com'.

    Raises:
        Exception: _description_
        Exception: _description_

    Returns:
        list: ['host1'...]
    """
    if default_domain is None:
        default_domain = configenv['DEFAULT_DOMAIN'] if 'DEFAULT_DOMAIN' in configenv else 'example.com'
    rslist = []
    if clients.find(',') > 0:
        rslistb = clients.split(',')
        for o in rslistb:
            clb = str(o).split(None)
            rslist = rslist + clb
    else:
        rslist = clients.split(None)
    newips = []
    for x in rslist:
        try:
            xreg = re.split(r'[\[\]:]', x)
            checkip = xreg[0] + xreg[1]
            if is_valid_ipv4_address(checkip):
                rslist.remove(x)
                ipa = xreg[0]
                aa = len(xreg[1])
                bb = len(xreg[2])
                if aa == bb:
                    strlen = len(xreg[1])
                    for b in range(int(xreg[1]), int(xreg[2]) + 1):
                        ip = ipa + str(b).zfill(strlen)
                        newips.append(ip)
                else:
                    raise Exception(
                        'Please make sure like 64.68.103.1[12:15].')
        except Exception as E:
            continue

    newclients = []
    for i in rslist:
        m = re.split(r'[\[\]:]', i)
        if len(m) > 1:
            if len(m[1]) == len(m[2]):
                for n in range(int(m[1]), int(m[2]) + 1):
                    newclients.append(m[0] + str(n).zfill(len(m[1])) + m[3])
            else:
                raise Exception(
                    'Build #{buildno}: Please make sure' +
                    ' like hostname0[10:19].')
        else:
            newclients.append(i)
    for n in range(len(newclients)):
        if len(str(newclients[n]).split('/')) > 1:
            continue
        if not is_valid_ipv4_address(newclients[n]) and not newclients[n].endswith(default_domain):
            newclients[n] = newclients[n] + '.' + default_domain

    covcls = newclients + newips
    if op == 'opdns':
        return covcls
    for client in covcls:
        if len(str(client).split('/')) > 1:
            continue
        if not is_valid_ipv4_address(client):
            try:
                socket.gethostbyname(client)
            except Exception as E:
                logger.debug(
                    f"This hostname: {client} can't be lookuped, issue: {E}")
    return covcls
