from setuptools import setup, find_packages

setup(
    name="transit-map-generator",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'typing-extensions>=4.0.0',
        'pathlib>=1.0.1',
        'svgwrite>=1.4.0',
        'json5>=0.9.0'
    ],
    entry_points={
        'console_scripts': [
            'transit-map=cli:main',
        ],
    },
) 
