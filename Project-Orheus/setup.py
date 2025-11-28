from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="project-orpheus",
    version="1.0.0",
    author="Divyansh",
    author_email="",
    description="AI-Powered Music Generation Studio with Premium UI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Divyansh-K-Art/Project-Orpheus",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Artistic Software",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "transformers>=4.35.2",
        "torch>=2.1.1",
        "scipy>=1.11.4",
        "numpy>=1.24.3",
        "python-multipart>=0.0.6",
        "pydantic>=2.5.0",
    ],
    entry_points={
        "console_scripts": [
            "orpheus=web_ui:main",
        ],
    },
)
