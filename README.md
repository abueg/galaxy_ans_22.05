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

PCRE: seems to be older unmaintained pcre 8.44 (not pcre2)
```
cd $STORE
wget --no-check-certificate https://downloads.sourceforge.net/project/pcre/pcre/8.44/pcre-8.44.tar.gz?ts=gAAAAABjBmQ4Rta323sOwWWFs88OXtEm9blG2Yau14JANqa7PRAVIuo0YF_-CwG4t73C9C_d2giMURHEvG4xc1ZE3yeTlZQMDQ%3D%3D&r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fpcre%2Ffiles%2Fpcre%2F8.44%2Fpcre-8.44.tar.gz%2Fdownload
mv pcre-8.44.tar.gz\?ts\=gAAAAABjBmQ4Rta323sOwWWFs88OXtEm9blG2Yau14JANqa7PRAVIuo0YF_-CwG4t73C9C_d2giMURHEvG4xc1ZE3yeTlZQMDQ\=\=  pcre-8.44.tar.gz
tar -xvzf pcre-8.44.tar.gz
mv pcre-8.44 pcre-8.44_src
mkdir pcre-8.44
./configure --prefix=$STORE/pcre-8.44
make
make install
```

zlib: using 1.2.11 as it's what's indicated in the example on nginx website
```
cd $STORE
wget https://github.com/madler/zlib/archive/refs/tags/v1.2.11.tar.gz
```

openssl: 1.1.1.g
```
cd $STORE
wget https://github.com/openssl/openssl/archive/refs/tags/OpenSSL_1_1_1g.tar.gz
```

symlinked their binaries in $STORE/bin/

download nginx source etc
```
### mainline
wget https://nginx.org/download/nginx-1.19.0.tar.gz
tar zxf nginx-1.19.0.tar.gz
### stable
wget https://nginx.org/download/nginx-1.18.0.tar.gz
tar zxf nginx-1.18.0.tar.gz
### renaming src and making install dirs
mv nginx-1.18.0/ ngi nx-1.18.0_src
mv nginx-1.19.0/ nginx-1.19.0_src

### conf / install
cd ../nginx-1.18.0_src/
./configure --prefix=$STORE/nginx-1.18.0 --with-pcre=$STORE/pcre-8.44 --with-zlib=$STORE/zlib-1.2.11 --user=vgl_galaxy --with-http_ssl_module --with-stream --with-debug --with-file-aio --with-http_gunzip_module --with-http_ssl_module --with-stream_ssl_module --with-threads
## ok that throws an error. lmfao

./configure --prefix=$STORE/nginx-1.19.0 --user=vgl_galaxy --with-http_ssl_module --with-stream --with-debug --with-http_gunzip_module --with-stream_ssl_module --with-threads
# checking for openat(), fstatat() ... found
# checking for getaddrinfo() ... found
# checking for PCRE library ... found
# checking for PCRE JIT support ... found
# checking for OpenSSL library ... found
# checking for zlib library ... found
# creating objs/Makefile
# 
# Configuration summary
#   + using threads
#   + using system PCRE library
#   + using system OpenSSL library
#   + using system zlib library
# 
#   nginx path prefix: "/lustre/fs5/vgl/store/vgl_galaxy//nginx-1.19.0"
#   nginx binary file: "/lustre/fs5/vgl/store/vgl_galaxy//nginx-1.19.0/sbin/nginx"
#   nginx modules path: "/lustre/fs5/vgl/store/vgl_galaxy//nginx-1.19.0/modules"
#   nginx configuration prefix: "/lustre/fs5/vgl/store/vgl_galaxy//nginx-1.19.0/conf"
#   nginx configuration file: "/lustre/fs5/vgl/store/vgl_galaxy//nginx-1.19.0/conf/nginx.conf"
#   nginx pid file: "/lustre/fs5/vgl/store/vgl_galaxy//nginx-1.19.0/logs/nginx.pid"
#   nginx error log file: "/lustre/fs5/vgl/store/vgl_galaxy//nginx-1.19.0/logs/error.log"
#   nginx http access log file: "/lustre/fs5/vgl/store/vgl_galaxy//nginx-1.19.0/logs/access.log"
#   nginx http client request body temporary files: "client_body_temp"
#   nginx http proxy temporary files: "proxy_temp"
#   nginx http fastcgi temporary files: "fastcgi_temp"
#   nginx http uwsgi temporary files: "uwsgi_temp"
#   nginx http scgi temporary files: "scgi_temp"
```
MY GUY WHERE DID YOU FIND THE SYSTEM LIBRARIES THEY'RE NOT INSTALLED ON A SYSTEM LEVEL THEY ARE SITTING IN A FOLDER NEXT TO YOU whatever
```
make
make install
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
