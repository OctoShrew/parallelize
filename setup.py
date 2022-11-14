from setuptools import setup
import pathlib

HERE = pathlib.Path(__file__).parent
INSTALL_REQUIRES = (HERE / "requirements.txt").read_text().splitlines()

setup(
   name='parallelize',
   version='0.1.0',
   author='OctoShrew Ltd.',
   author_email='felix.quinque@octoshrew.com',
   packages=['parallelize'],
   package_dir={'parallelize': 'src'},
   url='https://github.com/OctoShrew/parellelize',
   license='LICENSE',
   description='An easy to use parallelization library',
   long_description=open('README.md').read(),
   install_requires=INSTALL_REQUIRES,
)
