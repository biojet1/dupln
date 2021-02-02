import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dupln",
    version="0.0.2",
    author="biojet1",
    author_email="biojet1@gmail.com",
    description="Hard link files with same content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/biojet1/dupln",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": ["dupln=dupln.__main__:main"],
    },
    install_requires=["ocli"],
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)
