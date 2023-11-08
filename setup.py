from setuptools import find_packages, setup
from pathlib import Path

DESCRIPTION = "A Python wrapper library for ZKFinger fingerprint scanner software."

base_path = Path(__file__).parent
long_description = (base_path / "Readme.md").read_text()

setup(
    name='pyzkfp',
    packages=find_packages(),
    version='0.0.3',
    license="GPLv3",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Amjed Alqasemi',
    url='https://github.com/alqasemy2020/pyzkfp',
    author_email='alqasemy2020@gmail.com',
    install_requires=['pythonnet', 'PIL'],
    keywords=['python', 'fingerprint', 'scanner', 'wrapper', 'library', 'zkteco', 'zkfinger', 'zkfp', 'zklib', 'zkaccess', 'zktime'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
    package_dir={
        "": "pyzkfp"
    },
)