from setuptools import setup, find_packages

setup(
    name="spyscraper-json",
    version="0.1.0",
    description="Output the SpyScraper result in JSON format",
    packages=find_packages(),
    py_modules=["ss_json_output"],
    include_package_data=True,
    package_data={
        "": ["useragents.txt"],
    },
    entry_points={
        "console_scripts": [
            "spyscraper-json=ss_json_output:main",
        ],
    },
    install_requires=[
        "whois",
        "phonenumbers",
        "bs4",
        "python-whois",
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3 License",
        "Operating System :: OS Independent",
    ]
)