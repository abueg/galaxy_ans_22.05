# vglgalaxy_scratchbook
scribbles

~~vglgalaxy machine should have postgresql as part of its build~~ will try local (as vgl_galaxy) postgres installation https://www.postgresql.org/about/news/install-a-local-non-root-postgresql-server-with-python-pip-2291/

IP 129.85.14.10

note: might at some point need to make symlink for `.cache` in $HOME

steps:
1) install miniconda3 (for python3)
2) install postgres (via pgenv)
3) install ansible (via pip)
4) install DRMAA (so galaxy install can find the DRMAA files)
5) install galaxy via ansible
6) install ephemeris (via virtualenv)
7) install tools using ephemeris and an old tool list
8) install gxadmin for monitoring (from github) 

```
curl -L https://github.com/galaxyproject/gxadmin/releases/latest/download/gxadmin > $STORE/programs/bin/gxdmin
chmod +x $STORE/programs/bin/gxadmin
echo "vglgalaxy.rockefeller.edu:*5432:galaxy" > ~/.pgpass

export PGHOST="vglgalaxy.rockefeller.edu"
export PGUSER="vgl_galaxy"
export PGDATABASE=galaxy
```

ssh from local to vglgalaxy
`ssh -l vgl_galaxy vglgalaxy`

0.1) set up aliases/envvars for my own sanity:
```
export SCRATCH=/lustre/fs5/vgl/scratch/vgl_galaxy/
export STORE=/lustre/fs5/vgl/store/vgl_galaxy/
alias sq='squeue -p vgl,vgl_bigmem -o "%.15A %.15u %.15P %.15R %.15T %.15M %.j" | tr -s \\t'
alias sb='sbatch -p vgl -n 1 -c 32'
alias "l=ls -lahF"
export PS1="[\u@\h \w]\$ "
```
(normally DRMAA_LIBRARY_PATH is also in my bashrc but maybe that will be different here idk `export DRMAA_LIBRARY_PATH=$STORE/programs/slurm-drmaa/slurm-drmaa-1.1.3/lib/libdrmaa.so`)


1) set up miniconda3 (installs python3; needed for ansible), adapted from hpc guide: https://hpcguide.rockefeller.edu/guides/conda.html
first sets miniconda3 up in ~, then moves it to scratch, and makes symlink in ~
```
cd $HOME
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
mv miniconda3 /lustre/fs5/vgl/scratch/vgl_galaxy/miniconda3
ln -s /lustre/fs5/vgl/scratch/vgl_galaxy/miniconda3
exit
ssh -l vgl_galaxy vglgalaxy
conda config --set auto_activate_base false
exit
```

2) install ansible (local)
let's just use pip because it's here
https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html
```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/ansible-2.13.3]$ ~/miniconda3/bin/python3 -m pip -V
pip 21.2.4 from /ru-auth/local/home/vgl_galaxy/miniconda3/lib/python3.9/site-packages/pip (python 3.9)
~/miniconda3/bin/python3 -m pip install --user ansible
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/ansible-2.13.3]$ ansible --version
ansible [core 2.13.3]
  config file = None
  configured module search path = ['/ru-auth/local/home/vgl_galaxy/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /ru-auth/local/home/vgl_galaxy/.local/lib/python3.9/site-packages/ansible
  ansible collection location = /ru-auth/local/home/vgl_galaxy/.ansible/collections:/usr/share/ansible/collections
  executable location = /ru-auth/local/home/vgl_galaxy/.local/bin/ansible
  python version = 3.9.12 (main, Apr  5 2022, 06:56:58) [GCC 7.5.0]
  jinja version = 3.1.2
  libyaml = True
```



# testing ansible galaxy install w/o miniconda3/postgresql roles
```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy]$ cat requirements.yml 
- src: galaxyproject.galaxy
  version: 0.9.16
- src: galaxyproject.nginx
  version: 0.7.0
- src: geerlingguy.pip
  version: 2.0.0
- src: usegalaxy_eu.certbot
  version: 0.1.5
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy]$ ansible-galaxy install -p roles -r requirements.yml 
Starting galaxy role install process
- downloading role 'galaxy', owned by galaxyproject
- downloading role from https://github.com/galaxyproject/ansible-galaxy/archive/0.9.16.tar.gz
- extracting galaxyproject.galaxy to /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy/roles/galaxyproject.galaxy
- galaxyproject.galaxy (0.9.16) was installed successfully
- downloading role 'nginx', owned by galaxyproject
- downloading role from https://github.com/galaxyproject/ansible-nginx/archive/0.7.0.tar.gz
- extracting galaxyproject.nginx to /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy/roles/galaxyproject.nginx
- galaxyproject.nginx (0.7.0) was installed successfully
- downloading role 'pip', owned by geerlingguy
- downloading role from https://github.com/geerlingguy/ansible-role-pip/archive/2.0.0.tar.gz
- extracting geerlingguy.pip to /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy/roles/geerlingguy.pip
- geerlingguy.pip (2.0.0) was installed successfully
- downloading role 'certbot', owned by usegalaxy_eu
- downloading role from https://github.com/usegalaxy-eu/ansible-certbot/archive/0.1.5.tar.gz
- extracting usegalaxy_eu.certbot to /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy/roles/usegalaxy_eu.certbot
- usegalaxy_eu.certbot (0.1.5) was installed successfully
```

```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy]$ cat ansible.cfg 
[defaults]
interpreter_python = /ru-auth/local/home/vgl_galaxy/miniconda3/bin/python3
inventory = hosts
retry_files_enabled = false

[ssh_connection]
pipelining = true
```

setting `ansible_connection=local` as we are running this playbook on the same machine
```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy]$ cat hosts
[galaxyservers]
129.85.14.10 ansible_connection=local ansible_user=vgl_galaxy
```

```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy]$ ansible-playbook galaxy.yml --check

PLAY [galaxyservers] *******************************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [129.85.14.10]

TASK [Install Dependencies] ************************************************************************************************************************************************
fatal: [129.85.14.10]: FAILED! => {"changed": false, "msg": "No package matching 'python3-psycopg2' found available, installed or updated", "rc": 126, "results": ["No package matching 'python3-psycopg2' found available, installed or updated"]}

PLAY RECAP *****************************************************************************************************************************************************************
129.85.14.10               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=0   

[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy]$ vim requirements.yml 
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy]$ ansible-galaxy install -p roles -r requirements.yml 
Starting galaxy role install process
- galaxyproject.galaxy (0.9.16) is already installed, skipping.
- galaxyproject.nginx (0.7.0) is already installed, skipping.
- geerlingguy.pip (2.0.0) is already installed, skipping.
- downloading role 'miniconda', owned by uchida
- downloading role from https://github.com/uchida/ansible-miniconda-role/archive/0.3.0.tar.gz
- extracting uchida.miniconda to /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy/roles/uchida.miniconda
- uchida.miniconda (0.3.0) was installed successfully
- usegalaxy_eu.certbot (0.1.5) is already installed, skipping.
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy]$ ansible-playbook galaxy.yml --check

PLAY [galaxyservers] *******************************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [129.85.14.10]

TASK [Install Dependencies] ************************************************************************************************************************************************
fatal: [129.85.14.10]: FAILED! => {"changed": false, "msg": "No package matching 'python3-psycopg2' found available, installed or updated", "rc": 126, "results": ["No package matching 'python3-psycopg2' found available, installed or updated"]}

PLAY RECAP *****************************************************************************************************************************************************************
129.85.14.10               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=0 
```




# playing around with local ansible -> remote host
```
brew install ansible

ansible all --list-hosts -i /Users/linelle/Documents/_sandbox/_ansible/hosts 
#  hosts (1):
#    129.85.14.10

ansible all -i hosts -m ping -u vgl_galaxy
#129.85.14.10 | SUCCESS => {
#    "ansible_facts": {
#        "discovered_interpreter_python": "/usr/bin/python"
#    },
#    "changed": false,
#    "ping": "pong"
}
```

using an inventory

```
[linelle@blaziken ~/Documents/_sandbox/_ansible]$ ansible myhosts -m ping -i inventory.yaml
vglgalaxy | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    },
    "changed": false,
    "ping": "pong"
}
[linelle@blaziken ~/Documents/_sandbox/_ansible]$ ansible-inventory -i inventory.yaml --list
{
    "_meta": {
        "hostvars": {
            "vglgalaxy": {
                "ansible_host": "129.85.14.10",
                "ansible_user": "vgl_galaxy"
            }
        }
    },
    "all": {
        "children": [
            "myhosts",
            "ungrouped"
        ]
    },
    "myhosts": {
        "hosts": [
            "vglgalaxy"
        ]
    }
}
```

making a playbook

```
[linelle@blaziken ~/Documents/_sandbox/_ansible]$ ansible-playbook -i inventory.yaml playbook.yaml

PLAY [My first play] *******************************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [vglgalaxy]

TASK [Ping my hosts] *******************************************************************************************************************************************************
ok: [vglgalaxy]

TASK [Print message] *******************************************************************************************************************************************************
ok: [vglgalaxy] => {
    "msg": "Hello world"
}

PLAY RECAP *****************************************************************************************************************************************************************
vglgalaxy                  : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

[linelle@blaziken ~/Documents/_sandbox/_ansible]$ cat playbook.yaml 
- name: My first play
  hosts: myhosts
  tasks:
    - name: Ping my hosts
      ansible.builtin.ping:
    - name: Print message
      ansible.builtin.debug:
        msg: Hello world
```
