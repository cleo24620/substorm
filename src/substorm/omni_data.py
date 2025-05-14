import os
import re
from typing import List

import numpy as np
import pandas as pd

import config
from crawler import Crawler


def rename_files_with_date_hyphen(directory_path: str, dry_run: bool = True):
    """
    Renames files in a specified directory by changing date patterns from 'YYYYMM' to 'YYYY-MM' within the filenames.

    For example: 'data_199901_report.txt' -> 'data_1999-01_report.txt'.

    Args:
        dry_run: If True, only print proposed changes. If False, perform actual renames.
    """
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found or is not a directory.")
        return

    date_pattern = re.compile(r"(\d{4})(0[1-9]|1[0-2])")
    replacement_format = r"\1-\2"

    print(f"\nScanning directory: {os.path.abspath(directory_path)}")
    if dry_run:
        print("--- DRY RUN MODE --- (No actual changes will be made)")
    else:
        print("--- LIVE MODE --- (Files will be renamed)")

    files_processed = 0
    potential_renames = 0
    actual_renames = 0
    skipped_due_to_conflict = 0
    skipped_due_to_error = 0

    for filename in os.listdir(directory_path):
        original_full_path = os.path.join(directory_path, filename)

        if os.path.isfile(original_full_path):
            files_processed += 1
            new_filename = date_pattern.sub(replacement_format, filename)

            if new_filename != filename:  # A change is proposed
                potential_renames += 1
                new_full_path = os.path.join(directory_path, new_filename)

                print(f"    Proposed: '{filename}' -> '{new_filename}'")

                if not dry_run:
                    if os.path.exists(new_full_path):
                        print(f"    SKIPPED: Target file '{new_filename}' already exits.")
                        skipped_due_to_conflict += 1
                    else:
                        try:
                            os.rename(original_full_path, new_full_path)
                            print("    RENAMED successfully.")
                            actual_renames += 1
                        except OSError as e:
                            print(f"    ERROR renaming: {e}")
                            skipped_due_to_error += 1

    print("\n--- Renaming Summary ---")
    print(f"Total files scanned: {files_processed}")
    if dry_run:
        print(f"Potential files to be renamed: {potential_renames}")
        print("Run again with 'dry_run' set to 'False' to perform the actual renaming.")
    else:
        print(f"Files successfully renamed: {actual_renames}")
        print(f"Files skipped due to target existed: {skipped_due_to_conflict}")
        print(f"Files skipped due to errors: {skipped_due_to_error}")


def process_data(original_dir_path: str, processed_dir: str, prefix: str, extensions: List[str]):
    os.makedirs(processed_dir, exist_ok=True)
    for extension in extensions:
        os.makedirs(os.path.join(processed_dir, extension), exist_ok=True)
    original_filenames = os.listdir(original_dir_path)
    print("--- Processing Data ---")
    for filename in original_filenames:
        skip = False  # Reset
        print(f"\nProcessing file: {filename}")
        filepath = os.path.join(original_dir_path, filename)
        df = pd.read_csv(filepath, sep=config.OMNI_ORIGINAL_DATA_SEP, names=config.HRO_1M_MODIFIED_VARS)

        # Select variables.
        df = df[config.SELECTED_VARS]

        # Rename selected variables.
        df = df.rename(columns=config.SELECTED_VARS_RENAMES)

        # timestamps index
        df['date'] = pd.to_datetime(df['Year'].astype(str) + df['Day'].astype(str), format='%Y%j')
        df['timestamps'] = df['date'] + pd.to_timedelta(df['Hour'], unit='h') + pd.to_timedelta(df['Minute'], unit='m')
        df = df.set_index('timestamps')
        df = df.drop(columns=['Year', 'Day', 'Hour', 'Minute', 'date'])

        # Replace fill values with NaNs.
        df_num_rows = len(df)
        for var, fill_value in config.HRO1_VARS_FILL_VALUE.items():
            df[var] = df[var].replace(fill_value, np.nan)

            # If the number of Nans exceeds the set value, no following processing will be performed.
            if df[var].isna().sum() > config.MAX_NAN_RATIO * df_num_rows:
                print(f"Too many NaNs in the '{var}' column. Not use this month's data.")
                skip = True
        if skip:
            continue
        df = df.interpolate()

        # Save processed files.
        sfn = filename.replace('omni_min', prefix + '_')
        sfn_root = os.path.splitext(sfn)[0]
        for extension in extensions:
            sfn = sfn_root + '.' + extension
            if extension == 'pkl':
                sfp = os.path.join(processed_dir, 'pkl', sfn)
                df.to_pickle(sfp)
            elif extension == 'csv':
                sfp = os.path.join(processed_dir, 'csv', sfn)
                df.to_csv(sfp, index=True)
            else:
                raise ValueError(f"Unsupported file extension: {extension}")
            print(f"Saved processed file: {sfn}")


def generate_yyyymm_pandas(prefix: str, extension: str, start_year: int, start_month: int, end_year: int,
                           end_month: int, num_months: int = 0, ) -> List[str]:
    """
    Generate a list of 'YYYYMM' strings using pandas.
    Specify either a full end date or num_days.

    Args:
        num_months: the total number of months to generate (inclusive).
        sep: The separator of the return filename.

    Returns:
        A list of strings in 'YYYYMM' format.
    """
    start_date_str = f"{start_year}-{start_month:02d}"
    if end_year > 0 and end_month > 0:
        end_date_str = f"{end_year}-{end_month:02d}"
        dates = pd.date_range(start=start_date_str, end=end_date_str, freq="ME")
    elif num_months > 0:
        dates = pd.date_range(start=start_date_str, periods=num_months, freq="M")
    else:
        raise ValueError("You must specify either 'end_year' and 'end_month' or num_days.")

    return [f"{prefix}_{date_obj.strftime('%Y-%m')}.{extension}" for date_obj in dates]


def generate_yyyymmdd_pandas(prefix: str, extension: str, start_year: int, start_month: int, start_day: int,
                             end_year: int, end_month: int, end_day: int, num_days: int = 0, ) -> List[str]:
    """
    Generate a list of 'YYYYMMDD' strings using pandas.
    Specify either a full end date or num_days.

    Args:
        num_days: the total number of days to generate (inclusive).

    Returns:
        A list of strings in 'YYYYMMDD' format.
    """
    start_date_str = f"{start_year}-{start_month:02d}-{start_day:02d}"
    if end_year > 0 and end_month > 0 and end_day > 0:
        end_date_str = f"{end_year}-{end_month:02d}-{end_day:02d}"
        dates = pd.date_range(start=start_date_str, end=end_date_str, freq="D")
    elif num_days > 0:
        dates = pd.date_range(start=start_date_str, periods=num_days, freq="D")
    else:
        raise ValueError("You must specify either a full date or num_days.")

    return [f"{prefix}_{date_obj.strftime('%Y-%m-%d')}.{extension}" for date_obj in dates]


def all_files_exits(filepaths: List[str]) -> bool:
    if not filepaths:
        return False
    for fp in filepaths:
        if not os.path.isfile(fp):
            return False
    return True


if __name__ == "__main__":
    # Check whether the original files exist.
    if not os.path.exists(config.OMNI_ORIGINAL_DATA_DIR):
        raise FileNotFoundError(f"Error: The path '{config.OMNI_ORIGINAL_DATA_DIR}' does not exist.")

    if not os.path.isdir(config.OMNI_ORIGINAL_DATA_DIR):
        raise NotADirectoryError(f"Error: The path '{config.OMNI_ORIGINAL_DATA_DIR}' is not a directory.")

    if not os.listdir(config.OMNI_ORIGINAL_DATA_DIR):
        crawler_omni = Crawler(base_url=config.HRO_MODIFIED_URL_M)
        links_texts = crawler_omni.get_links(html_tag=config.HTML_TAG_M, href=config.HREF_PATTERN_M)
        crawler_omni.download_files(links_texts, download_directory=config.OMNI_ORIGINAL_DATA_DIR)

    # Rename the filenames of original files.
    dry_run_input = input("Use dry run mode? (y/n): ").strip().lower()
    if dry_run_input == "y":
        rename_files_with_date_hyphen(directory_path=str(config.OMNI_ORIGINAL_DATA_DIR), dry_run=True)
    elif dry_run_input == "n":
        rename_files_with_date_hyphen(directory_path=str(config.OMNI_ORIGINAL_DATA_DIR), dry_run=False)
    else:
        raise ValueError("Invalid input. Please enter 'y' or 'n'.")

    # Check whether the processed files exist.
    pkl_dir = os.path.join(config.OMNI_PROCESSED_DATA_DIR, 'pkl')
    csv_dir = os.path.join(config.OMNI_PROCESSED_DATA_DIR, 'csv')
    process_filepaths = os.listdir(pkl_dir) + os.listdir(csv_dir)
    if not process_filepaths:
        process_data(original_dir_path=config.OMNI_ORIGINAL_DATA_DIR, processed_dir=config.OMNI_PROCESSED_DATA_DIR,
                     prefix=config.OMNI_PROCESSED_DATA_PREFIX, extensions=config.OMNI_PROCESSED_DATA_EXTENSIONS)
    else:
        print("All processed files already exits.")
