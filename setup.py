from setuptools import setup, find_packages

setup(
    name="dupln",
    version="0.0.7",
    author="biojet1",
    author_email="biojet1@gmail.com",
    description="Hard link files with same content",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/biojet1/dupln",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["dupln=dupln.__main__:main"],
    },
    install_requires=[],
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)
