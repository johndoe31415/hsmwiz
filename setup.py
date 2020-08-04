#!/usr/bin/env python3

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'nitrotool',
    description='Easy handling of NitroKey HSM USB Smard Card',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='@johndoe31415',
    url='https://github.com/johndoe31415/nitrotool',
    license='GPL-3.0',
    keywords="nitrokey hsm smardcard",
    scripts = [ 'nitrotool' ],
    py_modules=[
        'ActionChangePIN',
        'ActionCheckEngine',
        'ActionExplore',
        'ActionFormat',
        'ActionGenCSR',
        'ActionGetPublicKey',
        'ActionIdentify',
        'ActionInit',
        'ActionKeyGen',
        'ActionPutCRT',
        'ActionRemoveKey',
        'ActionUnblock',
        'ActionVerifyPIN',
        'BaseAction',
        'CmdTools',
        'FriendlyArgumentParser',
        'MultiCommand',
        'NitroKey',
        'PrefixMatcher',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Unix",
    ],
)
