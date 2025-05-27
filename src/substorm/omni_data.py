import os
import re
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

import config


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

    date_pattern = re.compile(r"_(\d{4})-(0[1-9]|1[0-2])")
    replacement_format = r"\1\2"

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


def process_data(original_filepath: Path, processed_dir: Path):
    print("--- Processing Data ---")
    print(f"\nProcessing file: {original_filepath.name}")
    df = pd.read_csv(original_filepath, sep=config.OMNI_ORIGINAL_DATA_SEP, names=config.HRO_1M_MODIFIED_VARS)

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
    for var, fill_value in config.HRO1_VARS_FILL_VALUE.items():
        df[var] = df[var].replace(fill_value, np.nan)

    # Save processed files.
    sfp = processed_dir / original_filepath.name
    df.to_csv(sfp, index=True)


def generate_yyyymm_pandas(prefix: str, extension: str, start_year: int, start_month: int, end_year: int,
                           end_month: int, num_months: int = 0) -> List[str]:
    """
    Generate a list of 'YYYYMM' strings using pandas.
    Specify either a full end date or num_days.

    Args:
        num_months: the total number of months to generate (inclusive).

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

    return [f"{prefix}{date_obj.strftime('%Y%m')}.{extension}" for date_obj in dates]


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


def split_df_by_day_and_save(df: pd.DataFrame,
                             output_dir: str = config.OMNI_DAY_DIR,
                             file_format: str = 'asc',
                             ):
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a pandas DatetimeIndex.")

    if df.empty:
        print("Input DataFrame is empty. No files will be created.")
        return

    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: '{output_dir}'")

    grouped_by_day = df.groupby(pd.Grouper(freq='D'))

    if not grouped_by_day:
        print("No daily groups found in the DataFrame. Ensure index has date information.")
        return

    file_count = 0
    for day_timestamp, daily_df in grouped_by_day:
        day_timestamp: pd.Timestamp
        if daily_df.empty:
            print(f"No data for {day_timestamp.date()}. Skipping file creation.")
            continue

        formatted_date = day_timestamp.strftime('%Y-%m-%d')
        filename = f"{formatted_date}{file_format}"
        output_path = os.path.join(output_dir, filename)

        if os.path.isfile(output_path):
            print(f"File '{filename}' already exists. Skipping file creation.")
            continue

        print(f"Processing data for {day_timestamp.date()}... Saving to {filename}")

        try:
            daily_df.to_csv(output_path, index=True)
            file_count += 1
        except Exception as e:
            print(f"Error saving file '{filename}': {e}")

    print(f"\nFinished splitting DataFrame. {file_count} daily file(s) created in '{output_dir}'.")


def get_href_links_texts(url, html_tag: str, href_regex_pattern: str, proxies: Optional[dict] = None, ):
    print("Get links.")

    # Requests
    try:
        if proxies:
            response = requests.get(url=url, proxies=proxies)
        else:
            response = requests.get(url)
        print("Request successfully.")
    except requests.RequestException as e:
        print(f"An error occurred: {e}.")
        return None

    # Find all 'html_tag' elements that contain 'href'.
    soup = BeautifulSoup(response.text, 'html.parser')
    link_elements = soup.find_all(html_tag, href=True)

    print("Extracting links and corresponding texts.")
    links_texts = []
    file_counts = 0
    compiled_regex = re.compile(href_regex_pattern)
    for link_element in link_elements:
        match = compiled_regex.match(link_element['href'])
        if not match:
            continue
        link = os.path.join(url, link_element['href'])
        text = link_element.get_text()
        print(f"Link: {link}, Text: {text}.")
        links_texts.append({'link': link, 'text': text})
        file_counts += 1
    if file_counts == 0:
        print("No files found.")
        return None
    else:
        print(f"{file_counts} files found.")
        return links_texts


def download_file(link: str, download_dir: str, filename: str, proxies: Optional[dict] = None, write_mode: str = 'wb',
                  chunk_size: int = 8192):
    filepath = os.path.join(download_dir, filename)
    if os.path.isfile(filepath):
        print(f"File '{filename}' already exists. Skipping download.")
        return

    print(f"Downloading file '{filename}'.")

    # Get
    # If I use proxy, the function will return SSL error. If I do not use proxy, the function will sometimes return Timeout error.
    if proxies:
        response = requests.get(url=link, proxies=proxies)
    else:
        response = requests.get(url=link)
    print("Request successfully.")

    with open(filepath, write_mode) as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
    print(f"File '{filename}' downloaded successfully.")
