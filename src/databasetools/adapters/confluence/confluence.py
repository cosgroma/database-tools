import os
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
        retries = Retry(total=1000, backoff_factor=0.1, status_forcelist=[502, 503, 504], allowed_methods=["POST", "GET"])
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
                f"While uploading to confluence to page with id: {parent_id}, and title: {title} with content:\n{content}"
            ) from e
        print(f'''Created page, "{new_title}"''')
        return new_page

    def delete_page(self, page_id: str):
        self.confluence_client.remove_page(page_id)

    def make_confluence_page_directory(self, title: str, parent_id: Optional[str] = None) -> dict:
        """Confluence response format:

        'id': '905782905',
        'type': 'page',
        'status': 'current',
        'title': 'bob_4',
        'space': {'id': 828211208,
                'key': 'SERGEANT',
                'name': 'SERGEANT',
                'status': 'current',
                'type': 'global',
                '_links': {'webui': '/display/SERGEANT',
                            'self': 'https://confluence.northgrum.com/rest/api/space/SERGEANT'},
                '_expandable': {'metadata': '',
                                'icon': '',
                                'description': '',
                                'retentionPolicy': '',
                                'homepage': '/rest/api/content/820476337'}},
        'history': {'latest': True,
                    'createdBy': {'type': 'known',
                                'username': 'N66011',
                                'userKey': '8aecb8078fa33f75018fe49de79d005c',
                                'profilePicture': {'path': '/images/icons/profilepics/default.svg',
                                                    'width': 48,
                                                    'height': 48,
                                                    'isDefault': True},
                                'displayName': 'Wei, Jeremy [US] (MS)',
                                '_links': {'self': 'https://confluence.northgrum.com/rest/api/user?key=8aecb8078fa33f75018fe49de79d005c'},
                                '_expandable': {'status': ''}},
                    'createdDate': '2024-08-01T14:28:58.958-07:00',
                    '_links': {'self': 'https://confluence.northgrum.com/rest/api/content/905782905/history'},
                    '_expandable': {'lastUpdated': '',
                                    'previousVersion': '',
                                    'contributors': '',
                                    'nextVersion': ''}},
        'version': {'by': {'type': 'known',
                            'username': 'N66011',
                            'userKey': '8aecb8078fa33f75018fe49de79d005c',
                            'profilePicture': {'path': '/images/icons/profilepics/default.svg',
                                            'width': 48,
                                            'height': 48,
                                            'isDefault': True},
                            'displayName': 'Wei, Jeremy [US] (MS)',
                            '_links': {'self': 'https://confluence.northgrum.com/rest/api/user?key=8aecb8078fa33f75018fe49de79d005c'},
                            '_expandable': {'status': ''}},
                    'when': '2024-08-01T14:28:58.958-07:00',
                    'message': '',
                    'number': 1,
                    'minorEdit': False,
                    'hidden': False,
                    '_links': {'self': 'https://confluence.northgrum.com/rest/experimental/content/905782905/version/1'},
                    '_expandable': {'content': '/rest/api/content/905782905'}},
        'ancestors': [],
        'position': -1,
        'container': {'id': 828211208,
                    'key': 'SERGEANT',
                    'name': 'SERGEANT',
                    'status': 'current',
                    'type': 'global',
                    '_links': {'webui': '/display/SERGEANT',
                                'self': 'https://confluence.northgrum.com/rest/api/space/SERGEANT'},
                    '_expandable': {'metadata': '',
                                    'icon': '',
                                    'description': '',
                                    'retentionPolicy': '',
                                    'homepage': '/rest/api/content/820476337'}},
        'body': {'storage': {'value': '<ac:structured-macro ac:name="children" '
                                    'ac:schema-version="2" '
                                    'ac:macro-id="9112ef0a-5bae-4849-82aa-63a6c19f6d5b" '
                                    '/>',
                            'representation': 'storage',
                            '_expandable': {'content': '/rest/api/content/905782905'}},
                '_expandable': {'editor': '',
                                'view': '',
                                'export_view': '',
                                'styled_view': '',
                                'anonymous_export_view': ''}},
        'extensions': {'position': 'none'},
        '_links': {'webui': '/display/SERGEANT/bob_4',
                    'edit': '/pages/resumedraft.action?draftId=905782905',
                    'tinyui': '/x/eSb9NQ',
                    'collection': '/rest/api/content',
                    'base': 'https://confluence.northgrum.com',
                    'context': '',
                    'self': 'https://confluence.northgrum.com/rest/api/content/905782905'},
        '_expandable': {'metadata': '',
                        'operations': '',
                        'children': '/rest/api/content/905782905/child',
                        'restrictions': '/rest/api/content/905782905/restriction/byOperation',
                        'descendants': '/rest/api/content/905782905/descendant'}
        """
        new_title = self.alias_name(title)
        new_page = self.confluence_client.create_page(self.space_key, new_title, r"{children}", parent_id, representation="wiki")
        self.confluence_client.set_page_label(new_page["id"], "folder")
        print(f'''Created page, "{new_title}"''')
        return new_page

    def add_confluence_attachments(self, resource_dir: Union[Path, str], page_id: str):
        resource_dir = Path(resource_dir)
        for item in os.listdir(resource_dir):
            item_path = resource_dir / item
            self.confluence_client.attach_file(filename=item_path, page_id=page_id)
