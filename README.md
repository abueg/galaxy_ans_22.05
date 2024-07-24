test
# set up notes for VGL galaxy instance

IP 129.85.14.10

note: might at some point need to make symlink for `.cache` in $HOME

### steps:
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

### 0.1) set up aliases/envvars for my own sanity:
```
export SCRATCH=/lustre/fs5/vgl/scratch/vgl_galaxy/
export STORE=/lustre/fs5/vgl/store/vgl_galaxy/
alias sq='squeue -p vgl,vgl_bigmem -o "%.15A %.15u %.15P %.15R %.15T %.15M %.j" | tr -s \\t'
alias sb='sbatch -p vgl -n 1 -c 32'
alias "l=ls -lahF"
export PS1="[\u@\h \w]\$ "
```
(normally DRMAA_LIBRARY_PATH is also in my bashrc but maybe that will be different here idk `export DRMAA_LIBRARY_PATH=$STORE/programs/slurm-drmaa/slurm-drmaa-1.1.3/lib/libdrmaa.so`)


### 1) set up miniconda3 
(installs python3; needed for ansible), adapted from hpc guide: https://hpcguide.rockefeller.edu/guides/conda.html
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

### 2) install postgreSQL 14.5 using pgenv
installing it in $STORE because it is small. first we install 14.5 using `pgenv`, then we switch to it (switch = exporting its bins to path)
```
cd $STORE
https://github.com/theory/pgenv.git
cd pgenv
./bin/pgenv build 14.5
./bin/pgenv switch 14.5

export PATH=/lustre/fs5/vgl/store/vgl_galaxy/pgenv/pgsql/bin:$PATH
export PGDATA=/lustre/fs5/vgl/scratch/vgl_galaxy/pg_data
# pg_data is where we will put the postgres data
```
starting up postgres
```
pg_ctl init
pg_ctl -l /lustre/fs5/vgl/scratch/vgl_galaxy/pg_logs/logfile start

pg_ctl start
# to stop pg and let processes finish up
pg_ctl stop -m smart

# connect to pg, using database postgres (the one it comes with)
psql -d postgres
```
edit the postgres config to listen for vglgalaxy.rockefeller.edu

make your `$PGDATA/pg_hba.conf` look like this:
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust
# IPv4 local connections:
host    all             all             127.0.0.1/32            trust
host    all             all             129.85.14.10/32		trust
# IPv6 local connections:
host    all             all             ::1/128                 trust
# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
host    replication     all             ::1/128                 trust
```
add this line to start of `$PGDATA/postgresql.conf`:
```
listen_addresses = 'localhost,129.85.14.10'
```
start up postgres
```
pg_ctl -l $SCRATCH/pg_logs/logfile start
pg_ctl status
pgsql -d postgres
```


### 3) install ansible (local)
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
### 4) install DRMAA
this is the API galaxy uses to talk to SLURM (instructions lifted from Jason's HPC wiki entry, thank you!)
```
SLURM_DRMAA_ROOT=$HOME/dev/slurm-drmaa   # or wherever you want to install it
mkdir -p $SLURM_DRMAA_ROOT/download
mkdir -p $SLURM_DRMAA_ROOT/build
cd $SLURM_DRMAA_ROOT/download
wget https://github.com/natefoo/slurm-drmaa/releases/download/1.1.3/slurm-drmaa-1.1.3.tar.gz
cd $SLURM_DRMAA_ROOT/build
tar -zxf $SLURM_DRMAA_ROOT/download/slurm-drmaa-1.1.3.tar.gz
cd $SLURM_DRMAA_ROOT/build/slurm-drmaa-1.1.3
./configure --prefix=$SLURM_DRMAA_ROOT/slurm-drmaa-1.1.3
make && make install
export DRMAA_LIBRARY_PATH=$SLURM_DRMAA_ROOT/slurm-drmaa-1.1.3/lib/libdrmaa.so
```
**NOTE FOR LATER**: eventually might need to add `galaxy_systemd_env: [DRMAA_LIBRARY_PATH="/ru-auth/local/home/vgl_galaxy/dev/slurm-drmaa/slurm-drmaa-1.1.3/lib/libdrmaa.so"]` to `group_vars/galaxy.yml` or add it to `templates/galaxy/config/job_conf.xml`:
```        
        <plugin id="slurm" type="runner" load="galaxy.jobs.runners.slurm:SlurmJobRunner">
            <param id="drmaa_library_path">/ru-auth/local/home/vgl_galaxy/dev/slurm-drmaa/slurm-drmaa-1.1.3/lib/libdrmaa.so</param>
        </plugin>
``` 

### 5) install galaxy via ansible
heavily referencing this GTN training: https://training.galaxyproject.org/training-material/topics/admin/tutorials/ansible-galaxy/tutorial.html

but with variables set as in group_vars and andible.cfg. notably, we are **not using ansible to install postgresql or miniconda**.
1) first download roles as specified in `requirements.yml`
2) create `ansible.cfg` as appropriate
3) then should be able to run the `galaxy.yml` playbook.

```
ansible-galaxy install -p roles -r requirements.yml
ansible-playbook galaxy.yml
```

### 6) install ephemeris (via virtualenv)
you might need to already have an admin account set up so that you can get the API key. more instructions in this training: https://training.galaxyproject.org/training-material/topics/admin/tutorials/tool-management/tutorial.html

```
virtualenv -p python3 ~/ephemeris_venv
. ~/ephemeris_venv/bin/activate
pip install ephemeris

# how to get tool list from existing instance:
get-tool-list -g "http://vglgalaxy.rockefeller.edu:8080" -o "vglgalaxy_tool_list_20220925.yml"`
# install tool list into your running instance:
shed-tools install -g https://your-galaxy -a <api-key> -t workflow_tools.yml
```

### adfa) nginx

# nginx prerequisites
reference: https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/#sources

july 2024 edit: installed a new nginx pointing to the src files instead of the libraries, maybe work? i can get it to serve an `index.html` so idk. not sure if i need to run `make install` in the src folders if nginx is going to install them anyway?
```
## pcre
wget github.com/PCRE2Project/pcre2/releases/download/pcre2-10.42/pcre2-10.42.tar.gz
tar -zxf pcre2-10.42.tar.gz
mkdir pcre_install
cd pcre2-10.42
./configure  --prefix=/lustre/fs5/vgl/store/vgl_galaxy/newnginx/pcre_install
make
make install

## zlib
wget https://www.zlib.net/zlib-1.3.1.tar.gz
tar -xvzf zlib-1.3.1.tar.gz
mkdir zlib_install
cd zlib-1.3.1
./configure --prefix=/lustre/fs5/vgl/store/vgl_galaxy/newnginx/zlib_install
make
make install

## openssl
wget http://www.openssl.org/source/openssl-1.1.1v.tar.gz
tar -zxf openssl-1.1.1v.tar.gz
mkdir openssl_install
openssl-1.1.1v
./Configure linux-x86_64 --prefix=/lustre/fs5/vgl/store/vgl_galaxy/newnginx/openssl_install/
make
make install

## nginx
cd nginx-1.26.1
./configure --prefix=/lustre/fs5/vgl/store/vgl_galaxy/newnginx/nginx_install --with-stream --with-http_ssl_module --with-pcre=../pcre2-10.42 --with-openssl=../openssl-1.1.1v --with-zlib=../zlib-1.3.1
```

add to end of `galaxyservers.yml`:
```
# NGINX
nginx_selinux_allow_local_connections: true
nginx_servers:
  - galaxy
nginx_enable_default_server: false
nginx_conf_http:
  client_max_body_size: 1g
  # gzip: "on" # This is enabled by default in Ubuntu, and the duplicate directive will cause a crash.
  gzip_proxied: "any"
  gzip_static: "on"   # The ngx_http_gzip_static_module module allows sending precompressed files with the ".gz" filename extension instead of regular files.
  gzip_vary: "on"
  gzip_min_length: 128
  gzip_comp_level: 6  # Tradeoff of better compression for slightly more CPU time.
  gzip_types: |
      text/plain
      text/css
      text/xml
      text/javascript
      application/javascript
      application/x-javascript
      application/json
      application/xml
      application/xml+rss
      application/xhtml+xml
      application/x-font-ttf
      application/x-font-opentype
      image/png
      image/svg+xml
      image/x-icon
```

### aasfsd 24july2024) upgrading galaxy versions to 24.x
going to target https://github.com/galaxyproject/galaxy/releases/tag/v24.0.2
```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy]$ galaxyctlenv 
(venv) [vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy]$ galaxyctl stop
```
backing up database first. command started 12:15am, finished by 12:22 am
```
cd $SCRATCH/pg_srvr_backups
pg_dump galaxy | gzip > galaxy_database-20240724-1215.sql.gz
```
changed release tag to 22.1 and ran playbook, errored out here:
```
TASK [galaxyproject.galaxy : Ensure pip is the desired release] ************************************************************************
skipping: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Ensure setuptools is latest working release (<58)] ********************************************************
skipping: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Install nodeenv if it doesn't exist] **********************************************************************
skipping: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Report preferred Node.js version] *************************************************************************
ok: [vglgalaxy.rockefeller.edu] => {
    "galaxy_node_version": "18.12.1"
}

TASK [galaxyproject.galaxy : Check if node is installed] *******************************************************************************
ok: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Collect installed node version] ***************************************************************************
ok: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Remove node_modules directory when upgrading node] ********************************************************
changed: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Install or upgrade node] **********************************************************************************
changed: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Install yarn] *********************************************************************************************
fatal: [vglgalaxy.rockefeller.edu]: FAILED! => {"changed": false, "cmd": "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/npm install --global yarn", "msg": "node: /usr/lib64/libm.so.6: version `GLIBC_2.27' not found (required by node)\nnode: /usr/lib64/libc.so.6: version `GLIBC_2.25' not found (required by node)\nnode: /usr/lib64/libc.so.6: version `GLIBC_2.28' not found (required by node)\nnode: /usr/lib64/libstdc++.so.6: version `CXXABI_1.3.9' not found (required by node)\nnode: /usr/lib64/libstdc++.so.6: version `GLIBCXX_3.4.20' not found (required by node)\nnode: /usr/lib64/libstdc++.so.6: version `GLIBCXX_3.4.21' not found (required by node)", "rc": 1, "stderr": "node: /usr/lib64/libm.so.6: version `GLIBC_2.27' not found (required by node)\nnode: /usr/lib64/libc.so.6: version `GLIBC_2.25' not found (required by node)\nnode: /usr/lib64/libc.so.6: version `GLIBC_2.28' not found (required by node)\nnode: /usr/lib64/libstdc++.so.6: version `CXXABI_1.3.9' not found (required by node)\nnode: /usr/lib64/libstdc++.so.6: version `GLIBCXX_3.4.20' not found (required by node)\nnode: /usr/lib64/libstdc++.so.6: version `GLIBCXX_3.4.21' not found (required by node)\n", "stderr_lines": ["node: /usr/lib64/libm.so.6: version `GLIBC_2.27' not found (required by node)", "node: /usr/lib64/libc.so.6: version `GLIBC_2.25' not found (required by node)", "node: /usr/lib64/libc.so.6: version `GLIBC_2.28' not found (required by node)", "node: /usr/lib64/libstdc++.so.6: version `CXXABI_1.3.9' not found (required by node)", "node: /usr/lib64/libstdc++.so.6: version `GLIBCXX_3.4.20' not found (required by node)", "node: /usr/lib64/libstdc++.so.6: version `GLIBCXX_3.4.21' not found (required by node)"], "stdout": "", "stdout_lines": []}

RUNNING HANDLER [galaxyproject.galaxy : galaxy mule restart] ***************************************************************************

RUNNING HANDLER [galaxyproject.galaxy : galaxy gravity restart] ************************************************************************

PLAY RECAP *****************************************************************************************************************************
vglgalaxy.rockefeller.edu  : ok=73   changed=10   unreachable=0    failed=1    skipped=22   rescued=0    ignored=0


[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ ldd --version
ldd (GNU libc) 2.17
Copyright (C) 2012 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
Written by Roland McGrath and Ulrich Drepper.
```
going to try to use nvm to install a more recent node version, see if that works?

```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/store/vgl_galaxy]$ wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
=> Downloading nvm from git to '/ru-auth/local/home/vgl_galaxy/.nvm'
=> Cloning into '/ru-auth/local/home/vgl_galaxy/.nvm'...
remote: Enumerating objects: 369, done.
remote: Counting objects: 100% (369/369), done.
remote: Compressing objects: 100% (315/315), done.
remote: Total 369 (delta 42), reused 165 (delta 27), pack-reused 0
Receiving objects: 100% (369/369), 368.22 KiB | 0 bytes/s, done.
Resolving deltas: 100% (42/42), done.
* (detached from FETCH_HEAD)
  master
=> Compressing and cleaning up git repository

=> Appending nvm source string to /ru-auth/local/home/vgl_galaxy/.bashrc
=> Appending bash_completion source string to /ru-auth/local/home/vgl_galaxy/.bashrc
=> Close and reopen your terminal to start using nvm or run the following to use it now:

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

## ran the above commands

nvm install 18.12.1

## lol ok disk quota exceeded on home i should have moved it. i will do that
## reinstalled in $STORE, it worked to install 18.12.1. reran playbook and it didn't work i think because it is looking specifically at the node in the venv folder blehhhhh
TASK [galaxyproject.galaxy : Report preferred Node.js version] *********************************************************************************************************************************************
ok: [vglgalaxy.rockefeller.edu] => {
    "galaxy_node_version": "18.12.1"
}

TASK [galaxyproject.galaxy : Check if node is installed] ***************************************************************************************************************************************************
ok: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Collect installed node version] ***********************************************************************************************************************************************
fatal: [vglgalaxy.rockefeller.edu]: FAILED! => {"changed": false, "cmd": ["/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node", "--version"], "delta": "0:00:00.003139", "end": "2024-07-24 17:25:35.935666", "msg": "non-zero return code", "rc": 1, "start": "2024-07-24 17:25:35.932527", "stderr": "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node: /usr/lib64/libm.so.6: version `GLIBC_2.27' not found (required by /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node)\n/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node: /usr/lib64/libc.so.6: version `GLIBC_2.25' not found (required by /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node)\n/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node: /usr/lib64/libc.so.6: version `GLIBC_2.28' not found (required by /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node)\n/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node: /usr/lib64/libstdc++.so.6: version `CXXABI_1.3.9' not found (required by /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node)\n/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node: /usr/lib64/libstdc++.so.6: version `GLIBCXX_3.4.20' not found (required by /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node)\n/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node: /usr/lib64/libstdc++.so.6: version `GLIBCXX_3.4.21' not found (required by /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node)", "stderr_lines": ["/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node: /usr/lib64/libm.so.6: version `GLIBC_2.27' not found (required by /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node)", "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node: /usr/lib64/libc.so.6: version `GLIBC_2.25' not found (required by /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node)", "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node: /usr/lib64/libc.so.6: version `GLIBC_2.28' not found (required by /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node)", "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node: /usr/lib64/libstdc++.so.6: version `CXXABI_1.3.9' not found (required by /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node)", "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node: /usr/lib64/libstdc++.so.6: version `GLIBCXX_3.4.20' not found (required by /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node)", "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node: /usr/lib64/libstdc++.so.6: version `GLIBCXX_3.4.21' not found (required by /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/node)"], "stdout": "", "stdout_lines": []}

PLAY RECAP *************************************************************************************************************************************************************************************************
vglgalaxy.rockefeller.edu  : ok=66   changed=3    unreachable=0    failed=1    skipped=26   rescued=0    ignored=0



```





