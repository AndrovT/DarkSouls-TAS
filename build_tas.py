"""
Script to build wheel and exe files.
"""
import shutil
import subprocess


def cleanup():
    flds = ['build', 'dist']
    for fld in flds:
        try:
            shutil.rmtree(fld)
        except FileNotFoundError:
            pass


def make_wheel():
    subprocess.run(['python', 'setup.py', 'bdist_wheel'], check=True)


def make_exe():
    subprocess.run(['pyinstaller', 'darksoulstas.spec'])


if __name__ == '__main__':
    cleanup()
    make_wheel()
    make_exe()
