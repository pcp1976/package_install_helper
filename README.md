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
* -m specifies which section of the modules.cfg entries you want to install
* -a specifies which section of the packages.cfg entries you want to install
* -l specifies the logging level (one of CRITICAL, ERROR, WARNING, INFO, DEBUG)

## Vagrantfile example
```
Vagrant.configure("2") do |config|
	config.vm.define  "pcp1976-ddns-net" do |pcp1976|
		pcp1976.vm.box = "bento/ubuntu-16.04"
		pcp1976.vm.network "private_network", ip: "192.168.100.94"
		pcp1976.vm.provider "virtualbox" do |vb|
			vb.memory = "2048"
      		vb.name = "pcp1976-ddns-net"
      		vb.cpus = 2
		end
		pcp1976.vm.provision :shell do |modules|
			modules.path = 'script/install.py'
			modules.args = '-m pcp1976 -a pcp1976 -l DEBUG'
		end
		pcp1976.vm.provision "puppet" do |puppet|
			puppet.manifest_file = "default.pp"
		end
	end
end
```
