from setuptools import setup, find_packages

setup(
    name="agentred-cli",
    version="1.0.0",
    description="AgentRed CLI - AI Red Teaming Platform Command-Line Interface",
    long_description=open("README.md", encoding="utf-8").read() if open("README.md", encoding="utf-8").readable() else "",
    author="AgentRed Team",
    author_email="team@agentred.io",
    url="https://github.com/agentred/cli",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "click>=8.1.0",
        "httpx>=0.27.0",
        "rich>=13.7.0",
        "agentred>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "agentred=agentred.cli:cli",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: System :: Shells",
    ],
    keywords="cli command-line ai security red-team",
)
