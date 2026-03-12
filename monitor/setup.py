"""
Setup script for AgentRed Monitor SDK
"""
from setuptools import setup, find_packages

setup(
    name="agentred-monitor",
    version="0.1.0",
    description="AgentRed real-time monitoring SDK for AI agents",
    long_description=open("README.md").read() if __name__ == "__main__" else "",
    long_description_content_type="text/markdown",
    author="AgentRed Team",
    author_email="team@agentred.io",
    url="https://github.com/agentred/monitor",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "aiohttp>=3.9.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "nlp": ["spacy>=3.7.0"],
        "ml": ["scikit-learn>=1.4.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="security monitoring ai agents red-teaming",
)
