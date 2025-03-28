from setuptools import setup, find_packages

setup(
    name="abluka",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pygame>=2.0.0",
    ],
    entry_points={
        'console_scripts': [
            'abluka=run_abluka:main',
        ],
    },
    author="Can KURT - Ubden® Akademi",
    author_email="can@ubden.com",
    description="Abluka - Ubden® Akademi Abluka PC Oyunu",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ubden/abluka-online",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 