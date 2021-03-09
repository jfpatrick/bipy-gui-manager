"""
setup.py for bipy_gui_manager.

For reference see
https://packaging.python.org/guides/distributing-packages-using-setuptools/

"""
from pathlib import Path
from setuptools import setup, find_packages


HERE = Path(__file__).parent.absolute()
with (HERE / 'README.md').open('rt') as fh:
    LONG_DESCRIPTION = fh.read().strip()

REQUIREMENTS: dict = {
    'core': [
        "pyphonebook",
        "pyasn1>=-0.4.6",  # IDK why this is necessary, check again later
        "six",
        "argcomplete",
    ],
    'test': [
        "pytest",
        "pytest-cov",
        "pytest-random-order",
    ],
    'dev': [
    ],
    'doc': [
        "sphinx",
        "acc-py-sphinx",
    ],
}

setup(
    name='bipy_gui_manager',
    version="0.4.0",

    author="Sara Zanzottera",
    author_email="sara.zanzottera@cern.ch",
    description="Project Manager for SY-BI Python GUIs",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='',

    packages=find_packages(),
    python_requires='>=3.6, <4',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],

    install_requires=REQUIREMENTS['core'],
    extras_require={
        **REQUIREMENTS,
        # The 'dev' extra is the union of 'test' and 'doc', with an option
        # to have explicit development dependencies listed.
        'dev': [req
                for extra in ['dev', 'test', 'doc']
                for req in REQUIREMENTS.get(extra, [])],
        # The 'all' extra is the union of all requirements.
        'all': [req for reqs in REQUIREMENTS.values() for req in reqs],
    },
    include_package_data=True,  # For 'install-project.sh'
    entry_points={
        'console_scripts': [
            'bipy-gui-manager=bipy_gui_manager.main:main',
        ],
    },
)
