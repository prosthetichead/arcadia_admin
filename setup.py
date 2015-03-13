import os
import sys
import datetime
from cx_Freeze import setup, Executable

def files_under_dir(dir_name):
    file_list = []
    for root, dirs, files in os.walk(dir_name):
        for name in files:
            file_list.append(os.path.join(root, name))
    return file_list

includefiles = [ 'arcadia_admin/', 'config.py', 'arcadia_admin.py']

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

dt = datetime.datetime.now()

main_executable = Executable("arcadia_admin.py", base=base, icon="arcadia_admin/static/favicon.ico")
main_executable_cmd = Executable("arcadia_admin.py", base=None, icon="arcadia_admin/static/favicon.ico", targetName="arcadia_admin_debug.exe")

setup(name="Arcadia_Admin",
      version="0.3." + dt.strftime('%m%d.%H%m'),
      description="Arcadia Web Interface",
      options={
          'build_exe': {
              'packages': ['jinja2.ext',
                           'flask_sqlalchemy',
                           'flask_wtf',
						   'wtforms',
                           'os',
                           'flask_sqlalchemy._compat',
                           'sqlalchemy.dialects.sqlite',
                           'sqlalchemy',
			  			   'arcadia_admin',
						   'email',
			  			   'PIL',
						   'requests'],
              'include_files': includefiles,
              'include_msvcr': True}},
      executables=[main_executable, main_executable_cmd], requires=['flask', 'wtforms'])