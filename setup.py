from setuptools import find_packages, setup

DESCRIPTION = "A Python wrapper library for ZKFinger fingerprint scanner software."

setup(
    name='pyzkfp',
    packages=find_packages(),
    version='0.0.2',
    description=DESCRIPTION,
    author='Amjed Alqasemi',
    url='https://github.com/alqasemy2020/pyzkfp',
    author_email='alqasemy2020@gmail.com',
    install_requires=['pythonnet', 'PIL'],
    keywords=['python', 'fingerprint', 'scanner', 'wrapper', 'library', 'zkteco', 'zkfinger', 'zkfp', 'zklib', 'zkaccess', 'zktime'],
)