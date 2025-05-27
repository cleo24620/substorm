import pandas as pd

import config
from substorm import determine
from substorm import omni_data

# # fixme: I cannot solve the crawler 'SSL' problem.
# # Create dirs
# os.makedirs(config.OMNI_ORIGINAL_DATA_DIR, exist_ok=True)
#
# # Crawler the uncrawled data
# downloaded_file_paths = [os.path.join(config.OMNI_ORIGINAL_DATA_DIR, fn) for fn in
#                          os.listdir(config.OMNI_ORIGINAL_DATA_DIR)]
# href_links_texts = omni_data.get_href_links_texts(url=config.OMNI_HRO_MODIFIED_URL_M, html_tag=config.HTML_TAG_M,
#                                                   href_regex_pattern=config.HREF_REGEX_PATTERN_M)
# for link_text in href_links_texts:
#     fn = link_text['text']
#     fp = os.path.join(config.OMNI_ORIGINAL_DATA_DIR, fn)
#     if os.path.isfile(fp):
#         print(f"File '{fn}' already downloaded.")
#         continue
#     omni_data.download_file(link_text['link'], download_dir=config.OMNI_ORIGINAL_DATA_DIR, filename=fn)

# Process
for fp in config.OMNI_ORIGINAL_DATA_DIR.iterdir():
    processed_fp = config.OMNI_PROCESSED_DATA_DIR / fp.name
    if not processed_fp.exists():
        omni_data.process_data(original_filepath=fp,
                               processed_dir=config.OMNI_PROCESSED_DATA_DIR)

# Split month files to day files
file_format = '.asc'
for fp in config.OMNI_PROCESSED_DATA_DIR.iterdir():
    df = pd.read_csv(fp, index_col=0)
    df.index = pd.to_datetime(df.index)
    grouped_by_day = df.groupby(pd.Grouper(freq='D'))
    for day_timestamp, daily_df in grouped_by_day:
        day_timestamp: pd.Timestamp
        formatted_date = day_timestamp.strftime('%Y-%m-%d')
        day_fn = f"{formatted_date}{file_format}"
        day_fp = config.OMNI_DAY_DIR / day_fn
        if not day_fp.exists():
            omni_data.split_df_by_day_and_save(df, output_dir=config.OMNI_DAY_DIR, file_format=file_format)
            break

# Save substorm list files
file_format = '.csv'
for fp in config.OMNI_DAY_DIR.iterdir():
    df = pd.read_csv(fp, index_col=0)
    df.index = pd.to_datetime(df.index)
    substorm_determine = determine.SubstormDetermine(timestamps=df.index.values, imf_bz=df['IMF_GSM_Bz'],
                                                     lower_electrojet_index=df['AL'],
                                                     lower_electrojet_index_median=config.AL_MEDIAN,
                                                     lower_electrojet_index_derivatives_median=config.AL_DERIVATIVES_MEDIAN,
                                                     nan_ratio_threshold=config.MAX_NAN_RATIO)
    if (substorm_determine.expansion_phase is None) and (substorm_determine.growth_phase is None) and (
            substorm_determine.recovery_phase is None):
        continue
    sfn = fp.stem + file_format
    sfp = config.OMNI_SUBSTORM_LIST_DIR / sfn
    if not sfp.exists():
        determine.save_list(expansion_phase=substorm_determine.expansion_phase,
                            recovery_phase=substorm_determine.recovery_phase,
                            growth_phase=substorm_determine.growth_phase, sdir=config.OMNI_SUBSTORM_LIST_DIR, sfn=sfn,
                            stype=
                            file_format)
