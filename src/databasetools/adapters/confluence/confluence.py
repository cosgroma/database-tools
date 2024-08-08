from pathlib import Path
from typing import Optional
from typing import Union

from atlassian.confluence import Confluence
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class ConfluenceManager:
    def __init__(self, confluence_url: str, confluence_space_key: str, confluence_username: str, confluence_api_token: str):
        session = Session()
        retries = Retry(total=1000, backoff_factor=0.1, status_forcelist=[502, 503, 504], allowed_methods=False)
        session.mount("https://", HTTPAdapter(max_retries=retries))
        self.confluence_client = Confluence(
            url=confluence_url, username=confluence_username, password=confluence_api_token, timeout=600, session=session
        )
        self.space_key = confluence_space_key

    def alias_name(self, title: str):
        numba = 1
        new_title = title
        while self.title_exists(new_title):
            new_title = title + "_" + str(numba)
            numba += 1
        return new_title

    def title_exists(self, title: str):
        result = self.get_confluence_page_id(title)
        return True if result else False

    def get_confluence_page_id(self, title: str) -> str:
        return self.confluence_client.get_page_id(self.space_key, title)

    def make_confluence_page(self, title: str, content: str, parent_id: str) -> dict:
        new_title = self.alias_name(title)
        try:
            new_page = self.confluence_client.create_page(self.space_key, new_title, content, parent_id)
            self.confluence_client.set_page_label(new_page["id"], "page")
        except Exception as e:
            raise Exception(
                f"While uploading to confluence under page with id: {parent_id}, and title: {title} with content:\n{content}"
            ) from e
        print(f'''Created page, "{new_title}"''')
        return new_page

    def update_confluence_page(self, page_id: str, title: str, content: str) -> dict:
        try:
            response = self.confluence_client.update_page(page_id, title, content)
        except Exception as e:
            raise Exception(f""" While uploading "{title}" to confluence.""") from e
        print(f'''Updated page, "{title}"''')
        return response

    def delete_page(self, page_id: str):
        self.confluence_client.remove_page(page_id)

    def make_confluence_page_directory(self, title: str, parent_id: Optional[str] = None) -> dict:
        print(f"""Uploading "{title}""")
        new_title = self.alias_name(title)
        new_page = self.confluence_client.create_page(self.space_key, new_title, r"{children}", parent_id, representation="wiki")
        self.confluence_client.set_page_label(new_page["id"], "folder")
        print(f'''\tCreated page, "{new_title}"''')
        return new_page

    def add_confluence_attachments(self, resource_dir: Union[Path, str], page_id: str) -> dict:
        resource_dir = Path(resource_dir)
        return self.confluence_client.attach_file(filename=resource_dir, page_id=page_id)
