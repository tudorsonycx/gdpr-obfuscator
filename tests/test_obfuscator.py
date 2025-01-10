import pytest
from moto import mock_aws
import boto3
from gdpr_obfuscator import obfuscate_file
import pandas as pd
from pandas.testing import assert_frame_equal
import json
import io
import os


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture(scope="function")
def s3(aws_credentials):
    with mock_aws():
        yield boto3.client("s3", region_name="eu-west-2")


@pytest.fixture
def create_bucket(s3):
    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
    )


@pytest.fixture
def create_files(s3, create_bucket):
    s3.put_object(
        Bucket="test-bucket",
        Key="test.csv",
        Body=b"Name,Email\nJohn Doe,john@example.com\nJane Doe,jane@example.com",
    )

    s3.put_object(
        Bucket="test-bucket",
        Key="test.json",
        Body=b'[{"Name": "John Doe", "Email": "john@example.com"}, {"Name": "Jane Doe", "Email": "jane@example.com"}]',
    )

    df = pd.DataFrame(
        {
            "Name": ["John Doe", "Jane Doe"],
            "Email": ["john@example.com", "jane@example.com"],
        }
    )
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    buf.seek(0)
    s3.put_object(Bucket="test-bucket", Key="test.parquet", Body=buf)


def test_obfuscate_csv_file(create_files):
    input_file = json.dumps(
        {"file_to_obfuscate": "s3://test-bucket/test.csv", "pii_fields": ["Email"]}
    )
    result = obfuscate_file(input_file)
    expected = b"Name,Email\nJohn Doe,*\nJane Doe,*\n"
    assert result == expected


def test_obfuscate_json_file(create_files):
    input_file = json.dumps(
        {"file_to_obfuscate": "s3://test-bucket/test.json", "pii_fields": ["Email"]}
    )
    result = obfuscate_file(input_file)
    expected = b'[{"Name":"John Doe","Email":"*"},{"Name":"Jane Doe","Email":"*"}]'
    assert result == expected


def test_obfuscate_parquet_file(create_files):
    input_file = json.dumps(
        {"file_to_obfuscate": "s3://test-bucket/test.parquet", "pii_fields": ["Email"]}
    )
    result = obfuscate_file(input_file)

    result_df = pd.read_parquet(io.BytesIO(result))
    expected_df = pd.DataFrame({"Name": ["John Doe", "Jane Doe"], "Email": ["*", "*"]})
    assert_frame_equal(result_df, expected_df)


def test_invalid_file_format():
    input_file = json.dumps(
        {"file_to_obfuscate": "s3://test-bucket/test.txt", "pii_fields": ["Email"]}
    )
    with pytest.raises(ValueError):
        obfuscate_file(input_file)


def test_missing_field(create_files):
    input_file = json.dumps(
        {"file_to_obfuscate": "s3://test-bucket/test.csv", "pii_fields": ["Phone"]}
    )
    with pytest.raises(KeyError):
        obfuscate_file(input_file)

    input_file = json.dumps(
        {"file_to_obfuscate": "s3://test-bucket/test.json", "pii_fields": ["Phone"]}
    )
    with pytest.raises(KeyError):
        obfuscate_file(input_file)

    input_file = json.dumps(
        {"file_to_obfuscate": "s3://test-bucket/test.parquet", "pii_fields": ["Phone"]}
    )
    with pytest.raises(KeyError):
        obfuscate_file(input_file)
