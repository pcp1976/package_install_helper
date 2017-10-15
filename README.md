# package_install_helper
Python script to simplify apt package and puppet module installation, built primarily for bootstrapping a vagrant box to a state ready for puppet to continue installing and configuring software.
## Getting Started
1. Git clone the script into a folder accessible by your vagrant box (I prefer a 'script' directory located next to the Vagrantfile).
2. Add the script to your Vagranfile provisioners: foo.path = 'script/install.py'
3. Supply the script with arguments: foo.args = '-m pcp1976 -a pcp1976 -l DEBUG'
4. Create two ini files next to the install.py script: modules.cfg and packages.cfg.
5. Add entries for the puppet modules you want to install in modules.cfg:
```
[pcp1976]
postgresql: puppetlabs-postgresql --version 4.9.0
hosts: chrekh-hosts
supervisor: ajcrowe-supervisord
```
6. Add entries for the apt packages you want to install in packages.cfg:
```
[pcp1976]
puppet: puppet
```

## Script configuration
-m specifies which section of the modules.cfg entries you want to install
-a specifies which section of the packages.cfg entries you want to install
-l specifies the logging level (one of ERROR, WARNING, INFO, DEBUG)
