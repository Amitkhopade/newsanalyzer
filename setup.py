from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="newsanalyzer",
    version="1.0.0",
    author="Amit Khopade",
    author_email="amit.khopade@outlook.com",
    description="AI-powered business news analysis tool using Claude AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Amitkhopade/newsanalyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "streamlit>=1.32.0",
        "anthropic>=0.18.1",
        "python-dotenv>=1.0.1",
        "pandas>=1.3.0",
        "plotly>=5.0.0",
        "tavily-python>=0.3.1",
        "yfinance>=0.2.36",
    ],
    entry_points={
        "console_scripts": [
            "newsanalyzer=app.App:main",
        ],
    },
)
