from setuptools import setup, find_packages

setup(
    name="agentred",
    version="1.0.0",
    description="AgentRed Python SDK — AI Red Teaming Platform",
    long_description=open("README.md", encoding="utf-8").read() if open("README.md", encoding="utf-8").readable() else "",
    author="AgentRed Team",
    author_email="team@agentred.io",
    url="https://github.com/agentred/sdk",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "httpx>=0.27.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "isort>=5.0",
            "mypy>=1.0",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="ai security red-team testing adversarial llm",
)
