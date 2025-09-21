from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="deep-researcher-agent",
    version="1.0.0",
    author="Sathish Madanu",
    author_email="sathish.madanu@gmail.com",
    description="An AI-powered research assistant for document analysis and question answering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sathish0416/Deep-Researcher-Agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "deep-researcher=run_app:main",
        ],
    },
    keywords="ai, nlp, document-analysis, research, question-answering, streamlit, transformers",
    project_urls={
        "Bug Reports": "https://github.com/sathish0416/Deep-Researcher-Agent/issues",
        "Source": "https://github.com/sathish0416/Deep-Researcher-Agent",
        "Documentation": "https://github.com/sathish0416/Deep-Researcher-Agent#readme",
    },
)
