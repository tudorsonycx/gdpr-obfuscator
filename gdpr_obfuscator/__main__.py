import argparse
from .obfuscator import obfuscate_file
import pandas as pd
import io


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

    obfuscated_file_bytes = obfuscate_file(args.file)
    extension = args.file[]
    print(extension)
    print(pd.read_csv(io.BytesIO(obfuscated_file_bytes)))


if __name__ == "__main__":
    main()
