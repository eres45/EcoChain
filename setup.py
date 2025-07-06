from setuptools import setup, find_packages

setup(
    name="ecochain-guardian",
    version="0.1.0",
    description="EcoChain Guardian - Monitoring and rewarding eco-friendly crypto mining operations",
    author="EcoChain Team",
    author_email="example@ecochain.example",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "web3>=5.30.0",
        "requests>=2.25.0",
    ],
    entry_points={
        'console_scripts': [
            'ecochain=ecochain.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 