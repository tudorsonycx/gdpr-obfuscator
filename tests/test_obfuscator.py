import pytest
from unittest.mock import patch
from obfuscator.obfuscator import obfuscate_file
import pandas as pd
from pandas.testing import assert_frame_equal
import json
import io


@pytest.fixture
def s3_client_mock():
    with patch("boto3.client") as mock:
        yield mock


def test_obfuscate_csv_file(s3_client_mock):
    s3_client_mock.return_value.get_object.return_value = {
        "Body": io.BytesIO(
            b"Name,Email\nJohn Doe,john@example.com\nJane Doe,jane@example.com"
        )
    }
    input_file = json.dumps(
        {"file_to_obfuscate": "s3://bucket/test.csv", "pii_fields": ["Email"]}
    )
    result = obfuscate_file(input_file)
    expected = b"Name,Email\nJohn Doe,*\nJane Doe,*\n"
    assert result == expected


def test_obfuscate_json_file(s3_client_mock):
    s3_client_mock.return_value.get_object.return_value = {
        "Body": io.BytesIO(
            b'[{"Name": "John Doe", "Email": "john@example.com"}, {"Name": "Jane Doe", "Email": "jane@example.com"}]'
        )
    }
    input_file = json.dumps(
        {"file_to_obfuscate": "s3://bucket/test.json", "pii_fields": ["Email"]}
    )
    result = obfuscate_file(input_file)
    expected = b'[{"Name":"John Doe","Email":"*"},{"Name":"Jane Doe","Email":"*"}]'
    assert result == expected


def test_obfuscate_parquet_file(s3_client_mock):

    df = pd.DataFrame(
        {
            "Name": ["John Doe", "Jane Doe"],
            "Email": ["john@example.com", "jane@example.com"],
        }
    )
    parquet_buffer = io.BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)

    s3_client_mock.return_value.get_object.return_value = {"Body": parquet_buffer}
    input_file = json.dumps(
        {"file_to_obfuscate": "s3://bucket/test.parquet", "pii_fields": ["Email"]}
    )
    result = obfuscate_file(input_file)

    result_df = pd.read_parquet(io.BytesIO(result))
    expected_df = pd.DataFrame({"Name": ["John Doe", "Jane Doe"], "Email": ["*", "*"]})
    assert_frame_equal(result_df, expected_df)


def test_invalid_file_format():
    input_file = json.dumps(
        {"file_to_obfuscate": "s3://bucket/test.txt", "pii_fields": ["Email"]}
    )
    with pytest.raises(ValueError):
        obfuscate_file(input_file)


def test_missing_field(s3_client_mock):
    s3_client_mock.return_value.get_object.return_value = {
        "Body": io.BytesIO(
            b"Name,Email\nJohn Doe,john@example.com\nJane Doe,jane@example.com"
        )
    }
    input_file = json.dumps(
        {"file_to_obfuscate": "s3://bucket/test.csv", "pii_fields": ["Phone"]}
    )
    with pytest.raises(KeyError):
        obfuscate_file(input_file)
