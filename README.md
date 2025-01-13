# GDPR Obfuscator

## Table of Contents
- [Description](#description)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Description
GDPR Obfuscator is a tool designed to obfuscate personally identifiable information (PII) in CSV, JSON, and Parquet files stored in AWS S3. This helps ensure compliance with GDPR and other data protection regulations by anonymizing sensitive data.

## Features
- Obfuscates PII fields in CSV, JSON, and Parquet files.
- Supports files stored in AWS S3.
- Easy to use command-line interface.

## Technologies Used
- Python 3
- Boto3
- Pandas

## Installation

### Method 1
1. Clone the repository:
    ```sh
    git clone https://github.com/tudorsonycx/gdpr-obfuscator.git
    ```
2. Navigate to the project directory:
    ```sh
    cd gdpr-obfuscator
    ```
3. Create a virtual environment:
    ```sh
    python3 -m venv venv
    ```
4. Activate the virtual environment:
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```
    - On Windows:
        ```sh
        .\venv\Scripts\activate
        ```
5. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
6. Install the package:
    - From the current directory:
        ```sh
        pip install .
        ```
    - From a different location:
        ```sh
        pip install /path/to/gdpr-obfuscator
        ```

### Method 2
1. Install the package directly from the repository:
    ```sh
    pip install git+https://github.com/tudorsonycx/gdpr-obfuscator.git
    ```

## Usage

### AWS Credentials
Before using the obfuscator, ensure that your AWS credentials are configured.

You can learn more at https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html

### Command Line Interface
To obfuscate a file using the command line interface, use the following command:
```bash
gdpr-obfuscator --file '{"file_to_obfuscate": "s3://<bucket>/<key>.<extension>", "pii_fields": ["field1", "field2"]}'
```
Replace `<bucket>`, `<key>`, `<extension>`, `field1`, and `field2` with appropriate values.

### Importing the module

If you want to use the package in your own Python code, you can import the module and use its functions. Here is an example:

```python
# Import the obfuscator module
from gdpr_obfuscator import obfuscate

# Define the file to obfuscate and the PII fields
file_to_obfuscate = "s3://<bucket>/<key>.<extension>"
pii_fields = ["field1", "field2"]

# Call the obfuscate function
obfuscate(file_to_obfuscate, pii_fields)
```

## License
This project is licensed under the MIT [License](LICENSE).
