from setuptools import setup, find_packages

setup(
    name="gdpr-obfuscator",
    version="0.1.0",
    author="Tudor Dura",
    author_email="tudorsonycx@gmail.com",
    description="A tool to obfuscate personally identifiable information (PII) in CSV, JSON, and Parquet files stored in AWS S3.",
    packages=find_packages(include=["gdpr_obfuscator"]),
    install_requires=[
        "boto3==1.35.95",
        "pandas==2.2.3",
        "pyarrow==18.1.0",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "gdpr-obfuscator=gdpr_obfuscator.__main__:main",
        ],
    },
    include_package_data=True,
)
