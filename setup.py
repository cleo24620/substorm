from setuptools import setup, find_packages

setup(
    name='substorm',
    version='0.1.0',
    package_dir={'': 'src'},  # Tell setuptools where to look for packages
    packages=find_packages(where='src'),  # Automatically find packages under 'src'
    python_requires='>=3.10',
)
