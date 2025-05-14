import os
import time

import requests
import yaml
from bs4 import BeautifulSoup


class Crawler:
    LINKS_YAML_FILENAME = "links.yaml"
    WRONGLOG_TXT_FILENAME = "wronglog.txt"
    DOWNLOAD_CHUNK_SIZE = 8192
    WRITE_MODE = "w"

    def __init__(self, base_url: str):
        self.base_url = base_url

    def ensure_directory_exists(self, directory_path: str) -> None:
        """Ensure the given directory exists, creating it if necessary."""
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

    def get_links(
            self, html_tag: str, href: str = ""
    ) -> list[dict[str, str]] | None:
        """Fetches links from the webpage based on HTML tag and an optional condition."""
        response = requests.get(self.base_url)
        if response.status_code != 200:
            print(f"请求失败，状态码：{response.status_code}")
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for _ in soup.find_all(html_tag, href=True):
            if href and (href not in _["href"]):
                continue
            link = _["href"]
            text = _.get_text()
            links.append({"link": link, "text": text})
        return links

    def save_links_to_yaml(
            self, links: list[dict[str, str]], save_directory: str = "./"
    ) -> None:
        """Saves the extracted links to a YAML file."""
        self.ensure_directory_exists(save_directory)
        with open(
                os.path.join(save_directory, self.LINKS_YAML_FILENAME),
                "w",
                encoding="utf-8",
        ) as file:
            yaml.dump(links, file, allow_unicode=True)

    def download_files(
            self, links: list[dict[str, str]], download_directory: str = "./"
    ) -> None:
        """Downloads files from the provided links."""
        self.ensure_directory_exists(download_directory)
        for link_info in links:
            filename = link_info["text"]
            filepath = os.path.join(download_directory, filename)
            if os.path.isfile(filepath):
                print(f"{filename} 已存在，跳过下载。\n")
                continue
            try:
                response = requests.get(
                    os.path.join(self.base_url, link_info["link"]), stream=True
                )
                if response.status_code != 200:
                    self.log_download_error(
                        download_directory,
                        filename,
                        f"HTTP 状态码是 {response.status_code}",
                    )
                    time.sleep(1)
                    continue
                self.download_file(response, filepath)
            except requests.RequestException as e:
                self.log_download_error(download_directory, filename, str(e))
                time.sleep(1)

    def download_file(self, response, filepath: str) -> None:
        """Downloads a single file given the response object and saves it to the specified path."""
        start_time = time.time()
        with open(filepath, self.WRITE_MODE) as file:
            for chunk in response.iter_content(chunk_size=self.DOWNLOAD_CHUNK_SIZE):
                file.write(chunk)
        time.sleep(1)  # Avoid frequent requests
        end_time = time.time()
        print(f"成功下载 {filepath}，耗时 {end_time - start_time} 秒。\n")

    def log_download_error(
            self, download_directory: str, filename: str, error_message: str
    ) -> None:
        """Logs the error of failed downloads."""
        with open(
                os.path.join(download_directory, self.WRONGLOG_TXT_FILENAME),
                "a",
                encoding="utf-8",
        ) as file:
            file.write(f"下载 {filename} 失败，错误信息：{error_message}\n")
        print(f"下载 {filename} 失败，错误信息：{error_message}\n")
