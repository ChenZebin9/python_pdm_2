import os
import shutil
from subprocess import (Popen, PIPE)


def create_dir(the_path):
    if not os.path.exists(the_path):
        print('创建 {0}'.format(the_path))
        os.mkdir(the_path)


# 当前的工作目录
cwd = os.getcwd()
print('当前的工作目录：{0}'.format(cwd))
# 默认的程序输出目录
db_dir = 'D:\\setup_rom\\python_pdm_2\\'

db_dir_1 = input('输入程序默认目录：')
if db_dir_1 != '':
    db_dir = db_dir_1
print('输出的目录为：' + db_dir)

version = '1.5'
distpath = '{0}\\dist\\'.format(db_dir)
workpath = '{0}\\build\\'.format(db_dir)
create_dir(db_dir)
create_dir(distpath)
create_dir(workpath)

cmd = 'pyinstaller ' \
      '--noconfirm ' \
      '--version-file=file_version_info.txt ' \
      '--distpath={1} ' \
      '--workpath={2} ' \
      '--onedir ' \
      '--windowed ' \
      '--icon=OPS_ING_MMI.ico' \
      ' Entry.py'.format(version, distpath, workpath)

print(cmd)
p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
p.wait()

files_2_copy = ['pdm_config.ini', 'rt_config.db', 'db\\greatoo_jj_5.db']
target_db_dir = '{0}Entry\\db\\'.format(distpath)
print(target_db_dir)
create_dir(target_db_dir)

for f in files_2_copy:
    print('From {0}'.format(f))
    t_f = '{0}Entry\\{1}'.format(distpath, f)
    print('To {0}'.format(t_f))
    shutil.copy(f, t_f)
    
# 复制DLL文件
target_dll_f = '{0}Entry\\dlls\\'.format(distpath)
shutil.copytree('{0}\\dlls'.format(cwd), target_dll_f)

print('Done!!')
input('Press any key to end ...')

""" 可以增加zip文件的功能 """
