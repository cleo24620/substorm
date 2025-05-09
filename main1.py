# encoding = UTF-8
"""
@USER: cleo
@DATE: 2024/10/16
@DESCRIPTION: make sure all the files needed download to the specified path. Otherwise, crawler them.
"""

# %%
from crawler.crawler import Crawler

from config import HRO_MODIFIED_URL_M, HTML_TAG_M, HREF_PATTERN_M

# %% store dir where the download files save
sdir = r"\\Diskstation1\file_three\Alfven wave\OMNIData"

# %% make an instance of class Crawler use the url
crawler_omni = Crawler(HRO_MODIFIED_URL_M)

# %% get the links and texts
links_texts = crawler_omni.get_links_texts(HTML_TAG_M, HREF_PATTERN_M)

# %% use the links and texts to download files to the specified dir
crawler_omni.download_files(links_texts, sdir=sdir)
