#!/usr/bin/env python
# install.py

import sys, subprocess, ConfigParser, os, argparse, logging

def build_logger(name, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        fh = logging.FileHandler( '/vagrant/script/' + name + '.log')
        fh.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
    
class PackageInstaller(object):
    def __init__(self, defaults, level):
        build_logger('PackageInstaller', level)
        self.logger = logging.getLogger('PackageInstaller')
        self.logger.debug('Entered __init__()')
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open('/vagrant/script/packages.cfg'))
        self.logger.debug('open packages.cfg')
        self.apt_pkg_names = self.config.items(defaults)
        pkg_report = [] 
        for x in self.apt_pkg_names:
            pkg_report.append(x[1])
        self.logger.info('apt_pkg_names={pkg_report}'.format(pkg_report=pkg_report))
        self.logger.debug('exit __init__()')    

        
    def install_apt(self, pkg_name):
        self.logger.debug('entered install_apt')
        pkg = self.cache[pkg_name]
        self.logger.debug('package name={pkg_name}'.format(pkg_name=pkg_name))
        if pkg.is_installed:
            self.logger.info("{pkg_name} already installed".format(pkg_name=pkg_name))
        else:
            self.logger.info("marking {pkg_name} for install".format(pkg_name=pkg_name))
            pkg.mark_install()
    
    def do_install(self):
        self.logger.debug('entered do_install')
        need_to_do_update=False
        check_cmd='dpkg --get-selections'
        installed_output = subprocess.check_output(check_cmd, shell=True)
        for pkg in self.apt_pkg_names:
            self.logger.debug('checking if {pkg} installed'.format(pkg=pkg[1]))
            if pkg[1] not in installed_output:
                need_to_do_update=True
                self.logger.debug('{pkg} triggered update'.format(pkg=pkg[1]))
                self.logger.info('need to update')

        if need_to_do_update:
            update_command="sudo apt-get update"
            exit_code = subprocess.Popen(update_command, shell=True).wait()
            
            if exit_code==0:
                self.logger.info('got {exit_code} from apt-get update'.format(exit_code=exit_code))
                self.cache = apt.cache.Cache()
                self.cache.update()
                self.logger.debug('updated apt cache')

                for pkg in self.apt_pkg_names:
                    self.install_apt(pkg[1])
                try:
                    self.logger.info('committing cache')
                    self.cache.commit()
                    self.logger.info('cache commited')
                except Exception, arg:
                    self.logger.error("Sorry, package installation failed [{err}]".format(err=str(arg)))
            else:
                self.logger.error('apt-get update returned {exit_code}, install may fail'.format(exit_code=exit_code))

class ModuleInstaller(object):
    def __init__(self, defaults, level):
        build_logger('ModuleInstaller', level)
        self.logger = logging.getLogger('ModuleInstaller')
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open('/vagrant/script/modules.cfg'))
        self.modules_names = self.config.items(defaults)

    def install_module(self, pkg_name):
        os.system("sudo puppet module install " + pkg_name)
    
    def do_install(self):
        self.logger.debug('entered do_install')
        check_cmd = "sudo puppet module list"
        installed_output = subprocess.check_output(check_cmd, shell=True)
        self.logger.info("installed modules=\n{installed_output}".format(installed_output=installed_output))
        for pkg in self.modules_names:
            self.logger.debug('check if installed')
            if str(pkg[1].split(' ', 1)[0]) not in installed_output:
                self.logger.info('going to install module {mod}'.format(mod=str(pkg[1])))
                self.install_module(pkg[1])
            else:
                self.logger.info('{mod} module already installed, leaving'.format(mod=str(pkg[1])))
                
def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', action='store', dest='apt_packages', help='package set to install')
    parser.add_argument('-m', action='store', dest='puppet_modules', help='puppet modules to install')
    parser.add_argument('-l', action='store', dest='log_level', help='logging level ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG")', default='INFO')
    a = parser.parse_args(args)
    build_logger('Install.py', a.log_level)
    logger = logging.getLogger('Install.py')
    global apt
    try:
        import apt as apt
    except:
        logger.info("Instaling python-apt")
        try:
            update_command="sudo apt-get update && sudo apt-get install python-apt"
            exit_code = subprocess.Popen(update_command, shell=True).wait()
            logger.info("Exit code: {exit_code}".format(exit_code=exit_code))
            if(exit_code == 0):
                import apt as apt
            else:
                raise Exception("Return code {exit_code} not 0 whilst attempting to install python-apt".format(exit_code==exit_code))
        except Exception, e:
            logger.critical("Could not install python-apt: {msg}".format(msg==str(e)))
            sys.exit("Could not install python-apt")
    
    if a.apt_packages is not None:
        logger.info("Instaling apt {apt_packages} package set".format(apt_packages=a.apt_packages))
        installer = PackageInstaller(a.apt_packages, a.log_level)
        installer.do_install()
    else:
        logger.warn('no apt packages in this run')
    
    if a.puppet_modules is not None:
        logger.info("Instaling puppet {apt_packages} module set".format(apt_packages=a.puppet_modules))    
        installer = ModuleInstaller(a.puppet_modules, a.log_level)
        installer.do_install()
    else:
        logger.warn('no puppet modules in this run')
    
if __name__ == "__main__":
    main(sys.argv[1:])