#!/usr/bin/env python
# install.py

import sys
import subprocess
import ConfigParser
import os
import argparse
import logging

apt = None


def build_logger(name, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        fh = logging.FileHandler( '/vagrant/script/' + name + '.log')
        fh.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)


class PackageInstaller(object):
    def __init__(self, defaults, level, ini):
        build_logger('PackageInstaller', level)
        self.logger = logging.getLogger('PackageInstaller')
        self.logger.debug('Entered __init__()')
        self.config = ConfigParser.ConfigParser()
        try:
            self.config.readfp(open(ini))
        except Exception as e:
            self.logger.error("Could not open config file for PackageInstaller")
            exit(1)
        self.logger.debug('open packages.cfg')
        self.apt_pkg_names = self.config.items(defaults)
        pkg_report = [] 
        for x in self.apt_pkg_names:
            pkg_report.append(x[1])
        self.logger.info('apt_pkg_names=%s}' % pkg_report)
        self.logger.debug('exit __init__()')    

    def install_apt(self, pkg_name):
        self.logger.debug('entered install_apt')
        pkg = self.cache[pkg_name]
        self.logger.debug('package name=%s}' % pkg_name)
        if pkg.is_installed:
            self.logger.info("%s already installed" % pkg_name)
        else:
            self.logger.info("marking %s for install" % pkg_name)
            pkg.mark_install()
    
    def do_install(self):
        self.logger.debug('entered do_install')
        need_to_do_update=False
        check_cmd = 'dpkg --get-selections'
        installed_output = subprocess.check_output(check_cmd, shell=True)
        for pkg in self.apt_pkg_names:
            self.logger.debug('checking if %s installed' % pkg[1])
            if pkg[1] not in installed_output:
                need_to_do_update=True
                self.logger.debug('%s triggered update' % pkg[1])
                self.logger.info('need to update')

        if need_to_do_update:
            update_command = "sudo apt-get update"
            exit_code = subprocess.Popen(update_command, shell=True).wait()
            
            if exit_code == 0:
                self.logger.info('got %s from apt-get update' % exit_code)
                cache = apt.cache.Cache()
                cache.update()
                self.logger.debug('updated apt cache')

                for pkg in self.apt_pkg_names:
                    self.install_apt(pkg[1])
                try:
                    self.logger.info('committing cache')
                    cache.commit()
                    self.logger.info('cache committed')
                except Exception as arg:
                    self.logger.error("Sorry, package installation failed [%s]" % str(arg))
            else:
                self.logger.error('apt-get update returned %s, install may fail' % exit_code)


class ModuleInstaller(object):
    def __init__(self, defaults, level, ini):
        build_logger('ModuleInstaller', level)
        self.logger = logging.getLogger('ModuleInstaller')
        self.config = ConfigParser.ConfigParser()
        try:
            self.config.readfp(open(ini))
        except Exception as e:
            self.logger.error("Could not open config file for ModuleInstaller")
            exit(1)
        self.modules_names = self.config.items(defaults)

    @staticmethod
    def install_module(pkg_name):
        os.system("sudo puppet module install " + pkg_name)
    
    def do_install(self):
        self.logger.debug('entered do_install')
        check_cmd = "sudo puppet module list"
        installed_output = subprocess.check_output(check_cmd, shell=True)
        self.logger.info("installed modules=\n{%s}" % installed_output)
        for pkg in self.modules_names:
            self.logger.debug('check if installed')
            if str(pkg[1].split(' ', 1)[0]) not in installed_output:
                self.logger.info('going to install module %s' % str(pkg[1]))
                self.install_module(pkg[1])
            else:
                self.logger.info('%s module already installed, leaving' % str(pkg[1]))


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', action='store', dest='apt_packages', help='package set to install')
    parser.add_argument('-x', action='store', dest='apt_ini', help='apt packages ini file path')
    parser.add_argument('-m', action='store', dest='puppet_modules', help='puppet modules to install')
    parser.add_argument('-y', action='store', dest='puppet_ini', help='puppet modules ini file path')
    parser.add_argument(
        '-l',
        action='store',
        dest='log_level',
        help='logging level',
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        default='INFO'
    )
    a = parser.parse_args(args)
    build_logger('Install.py', a.log_level)
    logger = logging.getLogger('Install.py')
    global apt
    try:
        import apt as apt
    except ImportError:
        logger.info("Installing python-apt")
        try:
            update_command = "sudo apt-get update && sudo apt-get install python-apt"
            exit_code = subprocess.Popen(update_command, shell=True).wait()
            logger.info("Exit code: %s" % exit_code)
            if exit_code == 0:
                import apt as apt
            else:
                raise Exception("Return code %s not 0 whilst attempting to install python-apt" % exit_code)
        except Exception as e:
            logger.critical("Could not install python-apt: %s" % str(e))
            sys.exit("Could not install python-apt")
    
    if a.apt_packages is not None:
        logger.info("Installing apt %s package set" % a.apt_packages)
        installer = PackageInstaller(a.apt_packages, a.log_level, a.apt_ini)
        installer.do_install()
    else:
        logger.warn('no apt packages in this run')
    
    if a.puppet_modules is not None:
        logger.info("Installing puppet %s module set" % a.puppet_modules)
        installer = ModuleInstaller(a.puppet_modules, a.log_level, a.puppet_ini)
        installer.do_install()
    else:
        logger.warning('no puppet modules in this run')


if __name__ == "__main__":
    main(sys.argv[1:])
