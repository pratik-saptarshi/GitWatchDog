from setuptools import setup, find_packages

setup(
    name='gitwatchdog',
    version='0.1.0',
    description='GitHub contributor behavior profiler',
    author='GitWatchdog Contributors',
    packages=find_packages(),
    install_requires=[
        'PyGithub',
        'matplotlib',
        'seaborn',
        'plotly',
        'click',
        'pandas',
    ],
    entry_points={
        'console_scripts': [
            'gitwatchdog=gitwatchdog.cli:main',
        ],
    },
)
