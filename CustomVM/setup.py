from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='customvm',
    version='1.0.0',
    author='MERO:TG@QP4RM',
    author_email='mero@ps.com',
    description='Advanced Virtual Machine with Custom Instruction Set and Multi-Layer Security',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/6x-u/CustomVM',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[],
    extras_require={
        'dev': ['build', 'twine', 'pytest'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Topic :: Security',
        'Topic :: Software Development :: Interpreters',
    ],
    keywords='vm virtual-machine bytecode obfuscation security encryption',
    project_urls={
        'Documentation': 'https://github.com/6x-u/CustomVM#readme',
        'Source': 'https://github.com/6x-u/CustomVM',
    },
    entry_points={
        'console_scripts': [
            'cvmbuild=customvm.cli_build:main',
            'cvmrun=customvm.cli_run:main',
            'cvmstandalone=customvm.cli_standalone:main',
            'cvmbatch=customvm.cli_batch:main',
        ],
    },
)
