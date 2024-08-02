## plan (whatever that means)

1. back up PG database :white_check_mark:
2. upgrade to v24 :white_check_mark:
3. fix whatever broke getting the upgrade to work :white_check_mark:
4. test workflows 
5. clean up jobs directory :white_check_mark:
6. probably automate cleaning up the jobs directory lol
7. rolling PG database backups 
8. update homepage

## 1) backing up database
```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy]$ galaxyctlenv 
(venv) [vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy]$ galaxyctl stop
```
backing up database first. command started 12:15am, finished by 12:22 am
```
cd $SCRATCH/pg_srvr_backups
pg_dump galaxy | gzip > galaxy_database-20240724-1215.sql.gz
```

## 2) upgrading galaxy version to 24.x
going to target https://github.com/galaxyproject/galaxy/releases/tag/v24.0.2


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

## ok compiled node from scratch and then sym linked to that node, from the venv folder
git clone https://github.com/nodejs/node
cd node
git checkout v18.12.1
lmodinit
module load gcc/9.3.0-wsvuxi
make
ln -s $STORE/node/node /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/venv/bin/node

## seems to get past that but then yarn error. maybe i will put the server somewhere else and rebuild it entirely and see if that fixes?
TASK [galaxyproject.galaxy : Collect installed node version] ***************************************************************************************************
**************************
ok: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Remove node_modules directory when upgrading node] ********************************************************************************
**************************
skipping: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Install or upgrade node] *********************************************************************************************************$
**************************
skipping: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Install yarn] ********************************************************************************************************************$
**************************
changed: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Include client build process] ****************************************************************************************************$
**************************
included: /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05/roles/galaxyproject.galaxy/tasks/_inc_client_build_make.yml for vglgalaxy.rockefeller.edu

TASK [galaxyproject.galaxy : Build client] ********************************************************************************************************************$
**************************
fatal: [vglgalaxy.rockefeller.edu]: FAILED! => {"changed": false, "cmd": "/usr/bin/gmake client-production-maps", "msg": "gmake: *** [client-node-deps] Error 1$
, "rc": 2, "stderr": "gmake: *** [client-node-deps] Error 1\n", "stderr_lines": ["gmake: *** [client-node-deps] Error 1"], "stdout": "Could not find yarn, whic$
 is required to build the Galaxy client.\\nIt should be shipped with Galaxy's virtualenv, but to install yarn manually please visit \\033[0;34mhttps://yarnpkg.$
om/en/docs/install\\033[0m for instructions, and package information for all platforms.\\n\nfalse;\n", "stdout_lines": ["Could not find yarn, which is required
to build the Galaxy client.\\nIt should be shipped with Galaxy's virtualenv, but to install yarn manually please visit \\033[0;34mhttps://yarnpkg.com/en/docs/i$
stall\\033[0m for instructions, and package information for all platforms.\\n", "false;"]}

RUNNING HANDLER [galaxyproject.galaxy : galaxy mule restart] **************************************************************************************************$
**************************

RUNNING HANDLER [galaxyproject.galaxy : galaxy gravity restart] ***********************************************************************************************$
**************************

PLAY RECAP ****************************************************************************************************************************************************$
**************************
vglgalaxy.rockefeller.edu  : ok=71   changed=7    unreachable=0    failed=1    skipped=26   rescued=0    ignored=0

```
ok i think i am just going to pick the server up and put it somewhere else, and try to rebuild in the same spot from scratch. how big is server
```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy]$ du -sh galaxy_srv/galaxy/
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-9x4j26r8’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-lvh_fehv’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-but4sa5e’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-0uturltg’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-25a40ud9’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-59n6ywfl’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-zvskwfhv’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-m8spk3_x’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-nnj380im’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-1zi8w17r’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-hihdaq33’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/tmp_rfd5q57’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-bs9bjj04’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-u9y4qxnd’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-acnz7bqu’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-giufe2xi’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-_cmihpo5’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-6kye_xrs’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-x5m6neb4’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-i2123_2w’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-sa4y9qdd’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-syt49ssk’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-8ymd3bj4’: No such file or directory
du: cannot access ‘galaxy_srv/galaxy/var/tmp/wgunicorn-i5ngnnqg’: No such file or directory
74T     galaxy_srv/galaxy/
```
ok big. what the hell is in there
```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy]$ du -sh galaxy_srv/galaxy/jobs/
74T     galaxy_srv/galaxy/jobs/
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy]$ du -sh galaxy_srv/galaxy/server
4.5G    galaxy_srv/galaxy/server
```
ok it's mostly the jobs folder. maybe i run clean-up script first.... or just remove `galaxy_srv/galaxy/server` and try the playbook? i should probably clean up anyway but i would like to do that with a working install to make sure nothing went weird. https://training.galaxyproject.org/training-material/topics/admin/tutorials/backup-cleanup/tutorial.html#hands-on-configuring-postgresql-backups looks like options to set up tmpwatch to remove the failed job dirs. 
```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy]$ gxadmin galaxy
Unknown command
gxadmin usage:

galaxy: Galaxy Administration

Local-only commands can be configured in /ru-auth/local/home/vgl_galaxy/.config/gxadmin-local.sh


    galaxy amqp-test <amqp_url>                           Test a given AMQP URL for connectivity
    galaxy cleanup [days]                                 Cleanup histories/hdas/etc for past N days (default=30)
    galaxy cleanup-jwd <working_dir> [1|months ago]       (NEW) Cleanup job working directories
    galaxy decode <encoded-id>                            Decode an encoded ID
    galaxy encode <encoded-id>                            Encode an ID
    galaxy fav_tools                                      Favourite tools in Galaxy DB
    galaxy fix-conda-env <conda_dir/envs/>                Fix broken conda environments
    galaxy ie-list                                        List GIEs
    galaxy ie-show [gie-galaxy-job-id]                    Report on a GIE [HTCondor Only!]
    galaxy migrate-tool-install-from-sqlite [sqlite-db]   Converts SQLite version into normal potsgres toolshed repository tables
    galaxy migrate-tool-install-to-sqlite                 Converts normal potsgres toolshed repository tables into the SQLite version

All commands can be prefixed with "time" to print execution time to stderr

help / -h / --help : this message. Invoke '--help' on any subcommand for help specific to that subcommand
Tip: Run "gxadmin meta whatsnew" to find out what's new in this release!
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy]$ gxadmin galaxy cleanup-jwd --help
galaxy cleanup-jwd -  (NEW) Cleanup job working directories

**SYNOPSIS**

    gxadmin galaxy cleanup-jwd <working_dir> [1|months ago]

**NOTES**

Scans through a provided job working directory subfolder, e.g.
job_working_directory/ without the 005 subdir to find all folders which
were changed less recently than N months.

 Then it takes the first 1000 entries and cleans them up. This was more
of a hack to handle the fact that the list produced by find is really
long, and the for loop hangs until it's done generating the list.
```
this is also worth a try

ok i'm going to move the `$GALAXY_SRV/server/` and `$GALAXY_SRV/venv/` folders and try to rebuild... no database stuff right now, will try after.
```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ mv $GALAXYSRV/server/ $SCRATCH/debug_24jul2024
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ mv $GALAXYSRV/venv/ $SCRATCH/debug_24jul2024
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ ansible-playbook galaxy.yml
...
TASK [galaxyproject.galaxy : Include path management tasks] ****************************************************************************************************
included: /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05/roles/galaxyproject.galaxy/tasks/paths.yml for vglgalaxy.rockefeller.edu

TASK [galaxyproject.galaxy : Create galaxy_root] ***************************************************************************************************************
ok: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Create additional privilege separated directories] ********************************************************************************
changed: [vglgalaxy.rockefeller.edu] => (item=/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv)
changed: [vglgalaxy.rockefeller.edu] => (item=/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//server)
ok: [vglgalaxy.rockefeller.edu] => (item=/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//config)
ok: [vglgalaxy.rockefeller.edu] => (item=/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//local_tools)
...
TASK [galaxyproject.galaxy : Collect installed node version] ***************************************************************************************************
skipping: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Remove node_modules directory when upgrading node] ********************************************************************************
ok: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Install or upgrade node] **********************************************************************************************************
changed: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Install yarn] *********************************************************************************************************************
fatal: [vglgalaxy.rockefeller.edu]: FAILED! => {"changed": false, "cmd": "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//venv/bin/npm install --global yarn", "msg": "node: /usr/lib64/libm.so.6: version `GLIBC_2.27' not found (required by node)\nnode: /usr/lib64/libc.so.6: version `GLIBC_2.25' not found (required by node)\nnode: /usr/lib64/libc.so.6: version `GLIBC_2.28' not found (required by node)", "rc": 1, "stderr": "node: /usr/lib64/libm.so.6: version `GLIBC_2.27' not found (required by node)\nnode: /usr/lib64/libc.so.6: version `GLIBC_2.25' not found (required by node)\nnode: /usr/lib64/libc.so.6: version `GLIBC_2.28' not found (required by node)\n", "stderr_lines": ["node: /usr/lib64/libm.so.6: version `GLIBC_2.27' not found (required by node)", "node: /usr/lib64/libc.so.6: version `GLIBC_2.25' not found (required by node)", "node: /usr/lib64/libc.so.6: version `GLIBC_2.28' not found (required by node)"], "stdout": "", "stdout_lines": []}

RUNNING HANDLER [galaxyproject.galaxy : galaxy mule restart] ***************************************************************************************************

RUNNING HANDLER [galaxyproject.galaxy : galaxy gravity restart]
```
ok that... puts it back to the same node error as before. maybe the yarn error was because linking to the node binary in venv doesn't link everything else needed?
```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ l $GALAXYSRV/venv/bin/n*
-rwxr-xr-x 1 vgl_galaxy vgl 1.1K Jul 26 15:35 /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/venv/bin/nib_chrom_intervals_to_fasta.py*
-rwxr-xr-x 1 vgl_galaxy vgl  864 Jul 26 15:35 /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/venv/bin/nib_intervals_to_fasta.py*
-rwxr-xr-x 1 vgl_galaxy vgl  268 Jul 26 15:35 /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/venv/bin/nib_length.py*
-rwxr-xr-x 1 vgl_galaxy vgl  83M Nov  4  2022 /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/venv/bin/node*
-rwxr-xr-x 1 vgl_galaxy vgl  258 Jul 26 15:35 /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/venv/bin/nodeenv*
lrwxrwxrwx 1 vgl_galaxy vgl    4 Jul 26 15:36 /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/venv/bin/nodejs -> node*
-rwxr-xr-x 1 vgl_galaxy vgl  285 Jul 26 15:35 /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/venv/bin/normalizer*
lrwxrwxrwx 1 vgl_galaxy vgl   38 Jul 26 15:36 /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/venv/bin/npm -> ../lib/node_modules/npm/bin/npm-cli.js*
lrwxrwxrwx 1 vgl_galaxy vgl   38 Jul 26 15:36 /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/venv/bin/npx -> ../lib/node_modules/npm/bin/npx-cli.js*
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ l $GALAXYSRV/venv/bin/y*
ls: cannot access /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/venv/bin/y*: No such file or directory
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ l $GALAXYSRV/venv/bin/core*
lrwxrwxrwx 1 vgl_galaxy vgl 45 Jul 26 15:36 /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/venv/bin/corepack -> ../lib/node_modules/corepack/dist/corepack.js*
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ which gcc
/rugpfs/fs0/ruit/store/ruitsoft/soft/spack_2020b/opt/spack/linux-rhel7-haswell/gcc-8.3.0/gcc-9.3.0-wsvuxinmwdi27tplqhqxoqpyu45sqq5i/bin/gcc
```
how is that sitll the nov 2022 node. 
```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ mkdir ../debug_24jul2024/nodeagain/
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ mv $GALAXYSRV/venv/bin/node ../debug_24jul2024/nodeagain/
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ ln -s $STORE/node/node $GALAXYSRV/venv/bin/node
## ran playbook again...
...
TASK [galaxyproject.galaxy : Report preferred Node.js version] *************************************************************************************************
ok: [vglgalaxy.rockefeller.edu] => {
    "galaxy_node_version": "18.12.1"
}

TASK [galaxyproject.galaxy : Check if node is installed] *******************************************************************************************************
ok: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Collect installed node version] ***************************************************************************************************
ok: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Remove node_modules directory when upgrading node] ********************************************************************************
skipping: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Install or upgrade node] **********************************************************************************************************
skipping: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Install yarn] *********************************************************************************************************************
changed: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Include client build process] *****************************************************************************************************
included: /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05/roles/galaxyproject.galaxy/tasks/_inc_client_build_make.yml for vglgalaxy.rockefeller.edu

TASK [galaxyproject.galaxy : Build client] *********************************************************************************************************************
changed: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Fetch client version] *************************************************************************************************************
ok: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Set client build version fact] ****************************************************************************************************
ok: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Ensure that client update succeeded] **********************************************************************************************
skipping: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Include error document setup tasks] ***********************************************************************************************
skipping: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Include Gravity setup tasks] ******************************************************************************************************
included: /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05/roles/galaxyproject.galaxy/tasks/gravity.yml for vglgalaxy.rockefeller.edu

TASK [galaxyproject.galaxy : Register Galaxy config with Gravity] **********************************************************************************************
ok: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Update Gravity process management files] ******************************************************************************************
ok: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Include systemd unit setup tasks (Galaxy)] ****************************************************************************************
skipping: [vglgalaxy.rockefeller.edu]

TASK [galaxyproject.galaxy : Include systemd unit setup tasks (Reports)] ***************************************************************************************
skipping: [vglgalaxy.rockefeller.edu]

RUNNING HANDLER [galaxyproject.galaxy : galaxy mule restart] ***************************************************************************************************
skipping: [vglgalaxy.rockefeller.edu]

RUNNING HANDLER [galaxyproject.galaxy : galaxy gravity restart] ************************************************************************************************
skipping: [vglgalaxy.rockefeller.edu]

PLAY RECAP *****************************************************************************************************************************************************
vglgalaxy.rockefeller.edu  : ok=77   changed=8    unreachable=0    failed=0    skipped=32   rescued=0    ignored=0

[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$
```
looks ok, but then `galaxyctl start` doesn't work, says there's no configured instances.
```
(venv) [vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ echo $GALAXY_CONFIG_FILE

(venv) [vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ export GALAXY_CONFIG_FILE=/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/config/galaxy.yml
(venv) [vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ galaxyctl list
Dynamic handlers are configured in Gravity but Galaxy is not configured to assign jobs to handlers dynamically, so these handlers will not handle jobs. Set the job handler assignment method in the Galaxy job configuration to `db-skip-locked` or `db-transaction-isolation` to fix this.
INSTANCE NAME       CONFIG PATH
_default_           /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/config/galaxy.yml
(venv) [vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ galaxyctl status
Dynamic handlers are configured in Gravity but Galaxy is not configured to assign jobs to handlers dynamically, so these handlers will not handle jobs. Set the job handler assignment method in the Galaxy job configuration to `db-skip-locked` or `db-transaction-isolation` to fix this.
supervisord is not running
```
the `galaxy.yml` file pointed at has `job_config_file: /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy//config/job_conf.xml` in it, so i'm not sure...? i guess i'll add this block: https://training.galaxyproject.org/training-material/topics/admin/tutorials/ansible-galaxy/tutorial.html#hands-on-job-conf which isn't present in my `group_vars/galaxyservers.yml`, maybe it was added more recently...

wait. i think that's going to use the variable inside that `.yml` file instead of just pointing to my existing config file template. i'll just try to see if it can spin up without having to do that....

ok that failed -- job handlers are marked as failed which i think can be expected given the warning, but celery & gunicorn logs have a key error about 's3':
```
galaxy.jobs DEBUG 2024-07-26 16:57:51,992 [pN:main,p:988,tN:MainThread] Done loading job configuration
Traceback (most recent call last):
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/server/lib/galaxy/webapps/galaxy/buildapp.py", line 60, in app_pair
    app = galaxy.app.UniverseApplication(global_conf=global_conf, is_webapp=True, **kwargs)
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/server/lib/galaxy/app.py", line 698, in __init__
    super().__init__(fsmon=True, **kwargs)
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/server/lib/galaxy/app.py", line 622, in __init__
    file_sources = ConfiguredFileSources(
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/server/lib/galaxy/files/__init__.py", line 148, in __init__
    file_sources = self._load_plugins_from_file(configured_file_source_conf.conf_file)
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/server/lib/galaxy/files/__init__.py", line 187, in _load_plugins_from_file
    return self._parse_plugin_source(plugin_source)
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/server/lib/galaxy/files/__init__.py", line 190, in _parse_plugin_source
    return self._plugin_loader.load_plugins(plugin_source, self._file_sources_config)
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/server/lib/galaxy/files/plugins.py", line 100, in load_plugins
    return load_plugins(
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/server/lib/galaxy/util/plugin_config.py", line 59, in load_plugins
    return __load_plugins_from_dicts(
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/server/lib/galaxy/util/plugin_config.py", line 129, in __load_plugins_from_dicts
    plugin = plugins_dict[plugin_type](**plugin_kwds)
KeyError: 's3'
```
maybe i'll try removing the `s3` sources from the `file_sources.yml`?
```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_ans_22.05]$ cp templates/galaxy/config/file_sources_conf.yml templates/galaxy/config/file_sources_conf_NOS3.yml
```
ok trying that after two false starts. need to remember to actually point to the right new file in `group_vars/galaxyservers.yml` and then actually. re run. the playbook lmao

ok that eliminates the `s3` error but now there are errors from tool XMLs buh... problematic ones:
- phenotype_association/sift.xml
- toolshed.g2.bx.psu.edu/repos/iuc/merqury/merqury/1.3+galaxy1 ( $SCRATCH/galaxy_srv/galaxy/var/shed_tools/toolshed.g2.bx.psu.edu/repos/iuc/merqury/39edec572bae/merqury/macros.xml )

removed those and SHE LIVES. but ok now let's fix her

## 3) fixing what broke
seems three main things needed to be changed before the instance could start:
1. `job_conf.{x/y}ml` seems to be included in the `galaxyservers.yml` now instead of as a `files/template`, at least the way the GTN tutorial is structured. see about putting that in the `yml` or if i can keep using the xml...
2. had to remove `s3` sources from `file_sources.yml`, which included all the AWS bucket sources with authentication required... see what the current way of doing that is
3. weird tool XMLs causing issues. deleted them but maybe i can uninstall them from the admin panel to make sure galaxy knows they're gone...? i don't use `sift` and the `merqury` version mentioned is outdated. 

for (1): i will try to migrate the job_conf.xml to this format and put it in the ansible set up: https://training.galaxyproject.org/training-material/topics/admin/tutorials/ansible-galaxy/tutorial.html#hands-on-job-conf
- added `yml` to the `galaxyservers.yml` file and commented out lines referring to `job_conf.xml`
- server builds but refuses to use the `yml` data, instead uses an old `job_conf.xml` file at `$GALAXYSRV/config/job_conf.xml`. confirmed this by making edit in that file, and then rebuilding server, and observing that new server reflects the change to that file. but i want it to use the yml.....
- maybe i'll just treat the yml like the xml file previously, and have it in `templates`. worth trying to see if it gets rid of the handler error...
- also updating to use a more recent version of the galaxy ansible role...
- ok that's working AND gets rid of the handler error, let's stick with that! :white_check_mark:
- the retry destinations are failing when i cancel them w/ `scancel` (which used to work to get them to resubmit to the new env):
```
galaxy.jobs.runners.drmaa DEBUG 2024-07-31 20:33:13,355 [pN:handler_0,p:16705,tN:SlurmRunner.monitor_thread] (111596/62055227) state change: job finished, but failed
galaxy.jobs.runners.slurm DEBUG 2024-07-31 20:33:13,396 [pN:handler_0,p:16705,tN:SlurmRunner.monitor_thread] Checking /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/jobs/000/111/111596/galaxy_111596.e for exceeded memory message from SLURM
galaxy.jobs.runners.slurm INFO 2024-07-31 20:33:13,398 [pN:handler_0,p:16705,tN:SlurmRunner.monitor_thread] (111596/62055227) Job was cancelled via SLURM (e.g. with scancel(1))
galaxy.jobs.runners ERROR 2024-07-31 20:33:13,403 [pN:handler_0,p:16705,tN:SlurmRunner.work_thread-2] Caught exception in runner state handler
Traceback (most recent call last):
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/server/lib/galaxy/jobs/runners/__init__.py", line 577, in _handle_runner_state
    handler(self.app, self, job_state)
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/server/lib/galaxy/jobs/runners/state_handlers/resubmit.py", line 38, in failure
    _handle_resubmit_definitions(resubmit_definitions, app, job_runner, job_state)
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/server/lib/galaxy/jobs/runners/state_handlers/resubmit.py", line 50, in _handle_resubmit_definitions
    condition = resubmit.get("condition", None)
AttributeError: 'str' object has no attribute 'get'
```
- will try with `condition: unknown`
- ok that works! :white_check_mark:

for (2): referring to the [usegalaxy ORG playbook, which uses a jinja template for `file_sources_conf.yml`](https://github.com/galaxyproject/usegalaxy-playbook/blob/main/env/common/templates/galaxy/config/file_sources_conf.yml.j2):

```
- type: s3fs
  label: Genome Ark
  id: genomeark
  doc: Access to Genome Ark open data on AWS.
  bucket: genomeark
  anon: true
  listings_expiry_time: 60

- type: s3fs
  label: Genome Ark EXPORT HERE
  requires_groups: GenomeArkExport
  id: genomeark_galaxy
  doc: Access to Genome Ark open data on AWS.
  bucket: genomeark
  writable: true
  secret: "{{ genomeark_galaxy_aws_secret_access_key }}"
  key: "{{ genomeark_galaxy_aws_access_key_id }}"
  listings_expiry_time: 60
```
so that template is referring to `genomeark_galaxy_aws_secret_{access_key/key_id}`, which shows up in [`vars.yml`](https://github.com/galaxyproject/usegalaxy-playbook/blob/ffa577ad186102f9507f5adad4f688482325df20/env/main/group_vars/galaxyservers/vars.yml#L16):
```
## these vars are defined in vault.yml
#
# used by: galaxyproject.galaxy (templating job_conf.yml)
galaxy_job_conf_amqp_url: "{{ vault_galaxy_job_conf_amqp_url }}"

# used by: object store config template
galaxy_icat_irods_password: "{{ vault_galaxy_icat_irods_password }}"
galaxy_minio_idc_access_key: "idc"
galaxy_minio_idc_secret_key: "{{ vault_galaxy_minio_idc_secret_key }}"

# file_sources_conf.yml
covid_crg_ftp_staging_user: "{{ vault_covid_crg_ftp_staging_user }}"
covid_crg_ftp_staging_passwd: "{{ vault_covid_crg_ftp_staging_passwd }}"
genomeark_galaxy_aws_secret_access_key: "{{ vault_genomeark_galaxy_aws_secret_access_key }}"
genomeark_galaxy_aws_access_key_id: "{{ vault_genomeark_galaxy_aws_access_key_id }}"
genomeark_vgl_aws_secret_access_key: "{{ vault_genomeark_vgl_aws_secret_access_key }}"
genomeark_vgl_aws_access_key_id: "{{ vault_genomeark_vgl_aws_access_key_id }}"
```

to edit the vault file: `ansible-vault edit group_vars/secret.yml`
- added credentials to that file
- ok i got it to work :white_check_mark: when the `file_sources_conf.yml` refers to the `vault_*` variable but it doesn't work when i try to have it like. passed through the variables in `galaxyservers.yml`

bonus surprise 4) updating the tools' conda & python thanks to björn:
- tools' conda was version 4.6.14, so over two years old
- ran `/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/condabin/conda update conda`
- it updated to 22.9.0, still not latest
- python version was 3.7.12, also not latest
- at this point, trying `conda update` or `conda install python=3.10` were NOT working. throwing error: `module 'lib' has no attribute 'X509_V_FLAG_CB_ISSUER_CHECK'` having to do with `[...]/_conda/lib/python3.7/site-packages/OpenSSL/`
- following this advice: https://github.com/conda/conda/issues/10405#issuecomment-786503274 i removed OpenSSL from site-packages
- then this: ` . /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/bin/activate && conda install python=3.10`
- it looked like it worked but the end of log had this:
```
charset-normalizer-3 | 46 KB     | ############################################################################################################################################################################################################################################################################################################################### | 100%
python-3.10.14       | 26.8 MB   | ############################################################################################################################################################################################################################################################################################################################### | 100%
brotli-python-1.1.0  | 341 KB    | ############################################################################################################################################################################################################################################################################################################################### | 100%
pycparser-2.22       | 103 KB    | ############################################################################################################################################################################################################################################################################################################################### | 100%
libuuid-1.41.5       | 27 KB     | ############################################################################################################################################################################################################################################################################################################################### | 100%
pycosat-0.6.6        | 85 KB     | ############################################################################################################################################################################################################################################################################################################################### | 100%
conda-22.11.1        | 913 KB    | ############################################################################################################################################################################################################################################################################################################################### | 100%
Preparing transaction: done
Verifying transaction: done
Executing transaction: done
Retrieving notices: ...working... failed
Traceback (most recent call last):
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/exceptions.py", line 1129, in __call__
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/cli/main.py", line 86, in main_subshell
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/cli/conda_argparse.py", line 93, in do_call
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/notices/core.py", line 78, in wrapper
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/notices/core.py", line 39, in display_notices
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/notices/http.py", line 42, in get_notice_responses
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/notices/http.py", line 40, in <genexpr>
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/concurrent/futures/_base.py", line 598, in result_iterator
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/concurrent/futures/_base.py", line 435, in result
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/concurrent/futures/_base.py", line 384, in __get_result
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/concurrent/futures/thread.py", line 57, in run
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/notices/http.py", line 42, in <lambda>
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/notices/cache.py", line 37, in wrapper
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/notices/http.py", line 58, in get_channel_notice_response
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/requests/sessions.py", line 546, in get
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/requests/sessions.py", line 533, in request
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/requests/sessions.py", line 646, in send
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/requests/adapters.py", line 416, in send
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/requests/adapters.py", line 228, in cert_verify
OSError: Could not find a suitable TLS CA certificate bundle, invalid path: /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/certifi/cacert.pem

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/bin/conda", line 13, in <module>
    sys.exit(main())
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/cli/main.py", line 129, in main
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/exceptions.py", line 1429, in conda_exception_handler
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/exceptions.py", line 1132, in __call__
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/exceptions.py", line 1172, in handle_exception
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/exceptions.py", line 1183, in handle_unexpected_exception
  File "/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/lib/python3.7/site-packages/conda/exceptions.py", line 1245, in print_unexpected_error_report
ModuleNotFoundError: No module named 'conda.cli.main_info'
```
... but:
```
ModuleNotFoundError: No module named 'conda.cli.main_info'
(base) [vgl_galaxy@vglgalaxy ~]$ which python
/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/var/dependencies/_conda/bin/python
(base) [vgl_galaxy@vglgalaxy ~]$ python --version
Python 3.10.14
```
- so using python3.10 now, and carrying on past the certificate error since it was for python3.7
- `conda update conda` worked after that

galaxy now running python 3.10 and conda 24.7 :snake:

## 5&6) cleaning job directory
björn suggested either tmpreaper or tmpwatch, going to try out tmpwatch
```
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/store/vgl_galaxy]$ yum search tmpwatch
Loaded plugins: product-id, search-disabled-repos, subscription-manager
========================================================================================== N/S matched: tmpwatch ===========================================================================================
tmpwatch.x86_64 : A utility for removing files based on when they were last accessed

  Name and summary matches only, use "search all" for everything.
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/store/vgl_galaxy]$ yumdownloader --destdir tmpwatch --resolve tmpwatch
Loaded plugins: product-id, subscription-manager
epel-local                                                                                                                                                                           | 3.6 kB  00:00:00
lustre_client_repo                                                                                                                                                                   | 2.9 kB  00:00:00
rhel78-provisioner                                                                                                                                                                   | 2.8 kB  00:00:00
ruhpc-provisioner                                                                                                                                                                    | 2.9 kB  00:00:00
--> Running transaction check
---> Package tmpwatch.x86_64 0:2.11-6.el7 will be installed
--> Finished Dependency Resolution
tmpwatch-2.11-6.el7.x86_64.rpm                                                                                                                                                       |  39 kB  00:00:00
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/store/vgl_galaxy]$ l tmpwatch/
total 8.5K
drwxr-xr-x  2 vgl_galaxy vgl 4.0K Aug  2 11:54 ./
drwxr-xr-x 23 vgl_galaxy vgl 4.0K Aug  2 11:53 ../
-rw-r--r--  1 vgl_galaxy vgl  40K Feb 18  2019 tmpwatch-2.11-6.el7.x86_64.rpm
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/store/vgl_galaxy]$ mkdir tmpwatch_install
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/store/vgl_galaxy]$ cd tmpwatch_install/ && rpm2cpio /lustre/fs5/vgl/store/vgl_galaxy/tmpwatch/tmpwatch-2.11-6.el7.x86_64.rpm | cpio -idv
./usr/bin/tmpwatch
./usr/sbin/tmpwatch
./usr/share/doc/tmpwatch-2.11
./usr/share/doc/tmpwatch-2.11/AUTHORS
./usr/share/doc/tmpwatch-2.11/COPYING
./usr/share/doc/tmpwatch-2.11/ChangeLog
./usr/share/doc/tmpwatch-2.11/NEWS
./usr/share/doc/tmpwatch-2.11/README
./usr/share/man/man8/tmpwatch.8.gz
119 blocks
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/store/vgl_galaxy/tmpwatch_install]$ ./usr/bin/tmpwatch --help
./usr/bin/tmpwatch: unrecognized option '--help'
tmpwatch 2.11 - (C) 1997-2009 Red Hat, Inc. All rights reserved.
This program may be freely redistributed under the terms of the
GNU General Public License version 2.

tmpwatch [-u|-m|-c] [-MUXadfqtvx] [--verbose] [--force] [--all] [--nodirs] [--nosymlinks] [--test] [--quiet] [--atime|--mtime|--ctime] [--dirmtime] [--exclude <path>] [--exclude-user <user>] [--exclude-pattern <pattern>] [--fuser] <hours-untouched> <dirs>
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/store/vgl_galaxy/tmpwatch_install]$ ln -s $(pwd)/usr/bin/tmpwatch $STORE/bin/tmpwatch

tmpwatch --atime --test 60d . 

### using this one in $GALAXYJOBDIR, excluding the `000` dir where all the recent jobs (May '24 onward) were run
tmpwatch --atime --verbose 90d . --exclude=/lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/jobs/000/

### lots of verbose output
[vgl_galaxy@vglgalaxy /lustre/fs5/vgl/scratch/vgl_galaxy/galaxy_srv/galaxy/jobs]$ du -sh .
7.2T	.
```
clean! :broom:

