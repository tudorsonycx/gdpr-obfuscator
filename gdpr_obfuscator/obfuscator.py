import boto3
import pandas as pd
import io
import re
import json
import time
import logging

logging.basicConfig(level=logging.INFO)


def obfuscate_file(input_file: str) -> bytes:
    """
    Obfuscates specified fields in a file stored in an S3 bucket.

    Args:
        input_file (str): A JSON string containing the keys 'file_to_obfuscate' and 'pii_fields'.
                          'file_to_obfuscate' should be an S3 URI in the format 's3://<bucket>/<key>.<extension>'.
                          'pii_fields' should be a list of fields to be obfuscated.

    Returns:
        bytes: The obfuscated file content as bytes.

    Raises:
        KeyError: If 'file_to_obfuscate' or 'pii_fields' keys are missing in the input JSON,
                  or if any of the specified fields are not found in the file.
        ValueError: If 'file_to_obfuscate' is not in the correct S3 URI format.
    """
    input_file = json.loads(input_file)
    file_to_obfuscate = input_file.get("file_to_obfuscate")
    pii_fields = input_file.get("pii_fields")
    if not file_to_obfuscate or not pii_fields:
        raise KeyError(
            "The input file must contain 'file_to_obfuscate' and 'pii_fields' keys"
        )
    s3_uri_pattern = re.compile(
        r"^s3://([a-z0-9.-]+)/((?:[a-z0-9.-]+/{0,1})+(?<!/).((?:(?:csv)|(?:json)|(?:parquet))))$"
    )

    match = s3_uri_pattern.match(file_to_obfuscate)
    if not match:
        raise ValueError(
            "The 'file_to_obfuscate' key must be in the format 's3://<bucket>/<key>.<extension>'"
        )
    bucket, file_key, file_extension = match.groups()

    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=bucket, Key=file_key)
    obj_body = obj["Body"]

    buf = io.BytesIO()

    start_time = time.time()

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

    logging.info(f"Obfuscation completed in {time.time() - start_time:.2f} seconds")

    return buf.getvalue()
