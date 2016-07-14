from distutils.core import setup

setup (
    name = "mist",
    version = "0.5.0",
    description = "Cog commands for AWS",
    author = "Kevin Smith",
    author_email = "kevin@operable.io",
    url = "https://github.com/cog-bundles/mist",
    packages = ["mist", "mist.commands"],
    install_requires = ["pycog3 (>=0.1.27)", "PyYAML (>=3.11)", "boto (==2.39.0)"],
    keywords = ["cog", "aws", "ec2", "s3", "cloud"],
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License"
    ]
)
