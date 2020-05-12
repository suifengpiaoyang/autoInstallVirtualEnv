# coding=utf-8

import os
import re
import sys
import logging

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.CRITICAL)

# centos 7 默认没有安装 pip
python_version = sys.version_info[0]
if python_version == 2:
    python_path = os.popen('which python2').read().strip()
    python_version_string = 'python2'
    pip_command = 'pip2'
    input = raw_input
    cmd = '''
yum install epel-release -y
yum install python-pip -y
pip install --upgrade pip
'''
    os.system(cmd)
elif python_version == 3:
    python_path = os.popen('which python3').read().strip()
    python_version_string = 'python3'
    pip_command = 'pip3'
else:
    print('此一键脚本不适合你的系统！')
    sys.exit()


def judge_package(name):
    cmd = '{} list | grep {}'.format(pip_command, name)
    result = os.popen(cmd).read()
    if name in result:
        return True
    else:
        return False


def get_package_path(package_name, python_version_string):
    cmd = 'find / -name {}'.format(package_name)
    logging.debug(cmd)
    package_path = None
    result = os.popen(cmd).readlines()
    logging.debug(result)
    for each in result:
        if package_name in each and python_version_string in each:
            package_path = each.strip()
    if package_path is None:
        for each in result:
            if package_name in each:
                package_path = each.strip()
    return package_path


def print_help():
    help_message = '''
--------------------------------------------------------------------
virtualenvwrapper 模块的使用方式

mkvirtualenv [虚拟环境名称]         创建虚拟环境
lsvirtualenv -b                     列出虚拟环境
workon [虚拟环境名称]               切换虚拟环境
deactivate                          退出虚拟环境
rmvirtualenv [虚拟环境名称]         删除虚拟环境
cdvirtualenv                        进入虚拟环境目录
cdsitepackages                      进入虚拟环境的site-packages目录
lssitepackages                      列出site-packages目录的所有软件包
---------------------------------------------------------------------
'''
    print(help_message)

config_file = '/root/.bashrc'
if os.path.exists(config_file):
    with open(config_file)as fl:
        data = fl.read()
    result = re.findall(r'WORKON_HOME=(.*)', data)
    if len(result) == 1:
        virtualenv_path = result[0]
        print('虚拟环境本已存在，文件总路径为：{},现在脚本停止。'.format(virtualenv_path))
        print_help()
        sys.exit()

# 1.安装
package_name = 'virtualenvwrapper'
if not judge_package(package_name):
    cmd = '{} install {}'.format(pip_command, package_name)
    os.system(cmd)

if not judge_package(package_name):
    print('{} 下载失败，请查明原因'.format(package_name))
    sys.exit()

# 2.创建虚拟环境总文件夹
virtualenv_path = '/usr/local/myenvs'
if not os.path.exists(virtualenv_path):
    os.makedirs(virtualenv_path)

# 3.新建软链接
search_package1 = 'virtualenv'
virtualenv_package_path = get_package_path(
    search_package1, python_version_string)
if virtualenv_package_path is None:
    print('没有找到 {}，请手动安装 {}'.format(search_package1, search_package1))
    sys.exit()
cmd = 'ln -s {} /usr/bin/virtualenv'.format(virtualenv_package_path)
os.system(cmd)
logging.debug('软链接命令：{}'.format(cmd))

# 4.编辑配置环境
config_file = '/root/.bashrc'
if not os.path.exists(config_file):
    print('配置文件 {} 不存在，请查明原因。'.format(config_file))
    sys.exit()
search_package2 = 'virtualenvwrapper.sh'
virtualenvwrapper_package_path = get_package_path(
    search_package2, python_version_string)
if virtualenvwrapper_package_path is None:
    print('没有找到 {}，请手动安装 virutalenvwrapper'.format(search_package2))
    sys.exit()

add_command = '''
VIRTUALENVWRAPPER_PYTHON={}
export WORKON_HOME={}
source {}
'''.format(python_path, virtualenv_path, virtualenvwrapper_package_path)
if os.path.exists(config_file):
    with open(config_file, 'a+')as fl:
        fl.seek(0)
        filedata = fl.read()
        if package_name not in filedata:
            fl.write(add_command)

# 5.重启配置文件生效
cmd = 'source {}'.format(config_file)
os.system(cmd)

print_help()
print('请手动执行 {} 以完成安装。\n'.format(cmd))
print('安装完成。')
