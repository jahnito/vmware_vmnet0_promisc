import subprocess
import os


def check_group(name_group: str) -> bool:
    with open('/etc/group', 'r') as groupslist:
        for line in groupslist:
            if line.split(':')[0] == name_group:
                return True
    return False


def check_user(name_group: str) -> bool:
    with open('/etc/group', 'r') as groupslist:
        for line in groupslist:
            if line.split(':')[0] == name_group and os.getlogin() in line:
                return True
    return False


def create_group(name_group: str, gid: str) -> bool:
    group = subprocess.run(f'sudo groupadd -g {gid} {name_group}', shell=True)
    return group.returncode == 0


def add_user_to_group(name_group: str) -> bool:
    usermod = subprocess.run(f'sudo usermod -aG {name_group} {os.getlogin()}', shell=True)
    return usermod.returncode == 0


def create_env(tpl_unit: str, tpl_bin: str, path_unit: str, path_bin: str, time: int, name_group: str) -> bool:
    if os.path.exists(path_unit) and os.path.exists(path_bin):
        print(f'unit {path_unit} and {path_bin} exist')
    else:
        with open(path_unit.split('/')[-1], 'w') as unit:
            unit.write(tpl_unit.format(path_bin))
        with open(path_bin.split('/')[-1], 'w') as bin:
            bin.write(tpl_bin.format(time, name_group))
        subprocess.run('sudo mv vmware-promisc.service /etc/systemd/system/', shell=True)
        subprocess.run('sudo mv vmware-promiscous /usr/local/bin/', shell=True)
        subprocess.run(f'sudo chmod +x {path_bin}', shell=True)
        subprocess.run('sudo systemctl enable vmware-promisc.service', shell=True)
    print('Sucess')


GROUP = 'promisc'
GID = '3000'
PATH_UNIT = '/etc/systemd/system/vmware-promisc.service'
PATH_BIN = '/usr/local/bin/vmware-promiscous'
TPL_UNIT = '''[Unit]
  Description=VMware set promiscous mode vmnet0

[Service]
  Type=oneshot
  ExecStart={}
  RemainAfterExit=true

[Install]
  WantedBy=multi-user.target'''

TPL_BIN='''#!/bin/bash
sleep {}
chgrp {} /dev/vmnet0
chmod g+rw /dev/vmnet0
'''

if __name__ == '__main__':
    if check_group(GROUP):
        print(f'Group {GROUP} exist')
    else:
        cg = create_group(GROUP, GID)
        if cg:
            print(f'Group {GROUP} created')
        else:
            print(f'Error! Group {GROUP} NOT created')
    if check_user(GROUP):
        print(f'User {os.getlogin()} in group {GROUP}')
    else:
        au = add_user_to_group(GROUP)
        if au:
            print(f'User {os.getlogin()} added to group {GROUP}')
        else:
            print(f'User {os.getlogin()} NOT added to group {GROUP}')
    create_env(TPL_UNIT, TPL_BIN, PATH_UNIT, PATH_BIN, 10, GROUP)
