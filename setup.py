from setuptools import find_packages, setup

__version__ = '0.0.1'
URL = 'https://github.com/tbohne/nesy_diag_bench'

with open('requirements.txt') as f:
    required = f.read().splitlines()

for i in range(len(required)):
    # adapt the repo references for setup.py usage
    if "https" in required[i]:
        pkg = required[i].split(".git")[0].split("/")[-1]
        required[i] = pkg + "@" + required[i]

setup(
    name='nesy_diag_bench',
    version=__version__,
    description='Neuro-symbolic diagnosis benchmark.',
    author='Tim Bohne',
    author_email='tim.bohne@dfki.de',
    url=URL,
    download_url=f'{URL}/archive/{__version__}.tar.gz',
    keywords=[
        'neural-networks',
        'knowledge-graphs',
        'neuro-symbolic-ai',
        'state-machine',
        'anomaly-detection',
        'fault-diagnosis'
    ],
    python_requires='>=3.7, <3.11',
    install_requires=required,
    packages=find_packages(),
    include_package_data=True,
)
