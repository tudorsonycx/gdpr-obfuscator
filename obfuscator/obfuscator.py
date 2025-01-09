import boto3
import pandas as pd
import io
import re
import json


def obfuscate_file(input_file: str) -> bytes:
    """
    Obfuscates the specified fields in a file stored in an S3 bucket.

    The input file must be a JSON string containing the following keys:
    - "file_to_obfuscate": A string in the format 's3://<bucket>/<key>.<extension>'
      where <extension> is one of 'csv', 'json', or 'parquet'.
    - "pii_fields": A list of strings representing the fields to be obfuscated.

    The function retrieves the file from the specified S3 bucket, obfuscates the
    specified fields by replacing their values with '*', and returns the obfuscated
    file as bytes.

    Args:
        input_file (str): A JSON string containing the file details and fields to obfuscate.

    Returns:
        bytes: The obfuscated file content.

    Raises:
        ValueError: If the file_to_obfuscate is not in the correct format.
        KeyError: If any of the specified fields are not found in the file.
    """
    input_file = json.loads(input_file)
    file_to_obfuscate = input_file["file_to_obfuscate"]
    if not (
        re.match(
            r"^s3://[^/]+/[^/]+.(?:(?:csv)|(?:json)|(?:parquet))$", file_to_obfuscate
        )
    ):
        raise ValueError(
            "The file_to_obfuscate must be in the format 's3://<bucket>/<key>.<extension>'"
            " where extension is one of 'csv', 'json', or 'parquet'"
        )

    bucket, file_key = file_to_obfuscate.split("s3://")[1].split("/", 1)
    file_extension = file_key[file_key.rfind(".") + 1 :]
    pii_fields = input_file["pii_fields"]

    s3 = boto3.client("s3", region_name="eu-west-2")
    obj = s3.get_object(Bucket=bucket, Key=file_key)
    obj_body = obj["Body"]

    buf = io.BytesIO()

    if file_extension == "csv":
        df = pd.read_csv(obj_body)
        for field in pii_fields:
            if field not in df.columns:
                raise KeyError(f"Field '{field}' not found in the CSV file")
            df[field] = "*"
        df.to_csv(buf, index=False)

    elif file_extension == "json":
        df = pd.read_json(obj_body, orient="records")
        for field in pii_fields:
            if field not in df.columns:
                raise KeyError(f"Field '{field}' not found in the JSON file")
            df[field] = "*"
        df.to_json(buf, orient="records", index=False)

    elif file_extension == "parquet":
        parquet_file = io.BytesIO(obj_body.read())
        df = pd.read_parquet(parquet_file)
        for field in pii_fields:
            if field not in df.columns:
                raise KeyError(f"Field '{field}' not found in the parquet file")
            df[field] = "*"
        df.to_parquet(buf, index=False)

    return buf.getvalue()
