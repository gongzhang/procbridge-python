import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="procbridge",
    version="1.1",
    author="Gong Zhang",
    author_email="gong@me.com",
    description="A super-lightweight IPC (Inter-Process Communication) protocol over TCP socket.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gongzhang/procbridge-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
