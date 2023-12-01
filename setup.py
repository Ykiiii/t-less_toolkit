from setuptools import setup, find_packages

setup(
    name='my_package',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'open3d',
        'opencv-python'
    ],
    entry_points={
        'console_scripts': [
            'my_package=my_package.__main__:main'
        ]
    }
)
