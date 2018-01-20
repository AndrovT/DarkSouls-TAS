from setuptools import setup, find_packages
from wheel.bdist_wheel import bdist_wheel

__version__ = '2.1.0b2'
__author__ = 'AndrovT, DavidCEllis'


# Wheel doesn't know it's platform specific - force it
# noinspection PyPep8Naming,PyAttributeOutsideInit
class platform_bdist_wheel(bdist_wheel):
    def finalize_options(self):
        super().finalize_options()
        self.root_is_pure = False


setup(
    name='ds_tas',
    version=__version__,

    packages=find_packages(),
    url='https://github.com/DavidCEllis/DarkSouls-TAS',
    license='',
    description='TAS Tools for Dark Souls',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Speedrunners / TAS',
        'Topic :: Video Games :: TAS',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    package_data={  # Include the compiled dll
        '': ['lib/taslib.dll'],
    },
    cmdclass={'bdist_wheel': platform_bdist_wheel}
)
