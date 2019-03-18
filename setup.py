import setuptools

setuptools.setup(
    name="scrapperize",
    version="0.1",
    author="Zygimantas Bagdzevicius",
    author_email="zbagdzevicius@gmail.com",
    description="scrappers",
    url="https://github.com/zbagdzevicius/scrapperize",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "python-slugify",
        "googletrans",
        "translate",
        "scrapy",
        "beautifulsoup4",
    ],
)

