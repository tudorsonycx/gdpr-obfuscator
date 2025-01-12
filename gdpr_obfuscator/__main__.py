import argparse
from .obfuscator import obfuscate_file
import json
import logging
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Obfuscate PII fields in S3 files.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--file",
        required=True,
        type=str,
        metavar="<json_string>",
        help=(
            "A JSON string specifying the S3 file to obfuscate. "
            "The JSON must contain the following keys:\n"
            "- 'file_to_obfuscate': A string in the format 's3://<bucket>/<key>.<extension>' "
            "where <extension> is one of 'csv', 'json', or 'parquet'.\n"
            "- 'pii_fields': A list of strings representing the fields to be obfuscated."
        ),
    )
    args = parser.parse_args()

    try:
        file_dict = json.loads(args.file)
    except json.JSONDecodeError:
        logging.error("The input file must be a valid JSON string.")
        sys.exit(1)

    try:
        obfuscated_file_bytes = obfuscate_file(args.file)
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)

    extension = file_dict["file_to_obfuscate"][
        file_dict["file_to_obfuscate"].rfind(".") + 1 :
    ]

    file_name = f"obfuscated.{extension}"
    with open(file_name, "wb") as f:
        f.write(obfuscated_file_bytes)


if __name__ == "__main__":
    main()
