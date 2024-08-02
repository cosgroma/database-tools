import os
from pathlib import Path
from typing import Optional
from typing import Union

from atlassian.confluence import Confluence
from requests_ratelimiter import LimiterSession


class ConfluenceManager:
    def __init__(self, confluence_url: str, confluence_space_key: str, confluence_username: str, confluence_api_token: str):
        session = LimiterSession(per_second=0.5)
        self.confluence_client = Confluence(
            url=confluence_url, username=confluence_username, password=confluence_api_token, session=session
        )
        self.space_key = confluence_space_key

    # def upload_pages(self, page_blocks: Union[List[DocBlockElement], DocBlockElement], root_page_title: Optional[str] = None) -> Dict[Path, Tuple[str, str]]:
    #     if isinstance(page_blocks, DocBlockElement):
    #         page_blocks = [page_blocks]

    #     uploaded_page_info: Dict[Path, Tuple[str, str]] = {}

    #     for page_block in page_blocks:
    #         children_ids = page_block.children
    #         block_list = self.get_children_block_tree_list(page_block)

    #         content, required_resources = FromDocBlock.render_docBlock(block_list, children_ids, resource_prefix="RESOURCE")
    #         content = image2cf(content)
    #         page_name = self.alias_name(page_block.name)

    #         root_page_title = "Test Page" if root_page_title is None else root_page_title
    #         try:
    #             self.make_confluence_page(page_name, content, self.get_confluence_page_id(root_page_title))
    #         except Exception as e:
    #             raise Exception(f"Whilst attempting to upload page {page_block}, with content {content}") from e
    #         page_id = self.get_confluence_page_id(page_name)
    #         self.download_and_upload_resource(required_resources, page_id)
    #         export_path = page_block.block_attr["export_relative_path"]
    #         print(f"Uploaded: {export_path} as {page_name}")
    #         uploaded_page_info[export_path] = (page_id, page_name)

    #     return uploaded_page_info

    # def get_children_block_tree_list(self, block: DocBlockElement) -> List[DocBlockElement]:
    #     children_ids = block.children
    #     child_blocks = []
    #     for id in children_ids:
    #         child_blocks.extend(self.get_block_tree_list(id))

    #     return child_blocks

    # def get_block_tree_list(self, id: ObjectId) -> List[DocBlockElement]:
    #     found_blocks = self.mongo_man.find_in_col(collection_name=self.collection_name, id=id)
    #     if len(found_blocks) != 1:
    #         raise RuntimeError(f"More than one block found in the database with id: {id}")
    #     else:
    #         print(f"Found block: {found_blocks[0].id}")
    #         block_list: List[DocBlockElement] = [found_blocks[0]]

    #     for id in block_list[0].children:
    #         block_list.extend(self.get_block_tree_list(id))

    #     return block_list

    # def upload_one_note_export_to_confluence(self, export_id: ObjectId, parent_id: str):
    #     existing_upload = self.mongo_man.find_in_col(self.con_col_name, id=export_id)

    #     if existing_upload:
    #         con_data: ConfluenceFileStruct = existing_upload[0]
    #         page_list = self.mongo_man.find_in_col(self.collection_name, type=DocBlockElementType.PAGE, export_id=export_id)
    #         page_key = con_data.page_key
    #     else:
    #         page_list, page_key = self._make_page_key(export_id, parent_id)

    #     try:
    #         for page in page_list:
    #             page_path = Path(page.block_attr["export_relative_path"])
    #             _, parent_confluence_page_name = page_key[page_path.parent]

    #             upload_info = self.upload_pages(page, parent_confluence_page_name)
    #             page_key = {**page_key, **upload_info}
    #     except Exception as e:
    #         raise Exception(f"While uploading export {export_id}, under confluence page with id {parent_id}") from e
    #     finally:
    #         new_page_key = self.page_key_to_string(page_key)
    #         print(new_page_key)
    #         upload_metadata = ConfluenceFileStruct(
    #             id = export_id,
    #             name = page_list[0].block_attr["export_name"],
    #             page_key = new_page_key,
    #             upload_time = datetime.now(),
    #         )
    #         self.mongo_man.upload_to_col(self.con_col_name, upload_metadata)

    # def _make_page_key(self, export_id: ObjectId, parent_page_id: Optional[str] = None) -> Tuple[List[DocBlockElement], Dict[Path, Tuple[str, str]]]:
    #     """_summary_

    #     Args:
    #         export_id (ObjectId): _description_
    #         parent_page_id (Optional[str], optional): _description_. Defaults to None.

    #     Returns:
    #         Tuple[List[DocBlockElement], Dict[Path, Tuple[str, str]]]:
    #     """
    #     page_list: List[DocBlockElement] = self.mongo_man.find_in_col(collection_name=self.collection_name, type=DocBlockElementType.PAGE, export_id=export_id)
    #     print(page_list)
    #     print(f"Making {len(page_list)} pages.......")

    #     export_name = self.alias_name(page_list[0].block_attr.get("export_name"))
    #     root_page = self.make_confluence_page_directory(export_name, parent_page_id)
    #     path_list = set(path for page in page_list for path in Path(page.block_attr["export_relative_path"]).parents)
    #     page_key = {path: None for path in path_list}
    #     page_key[Path(".")] = (root_page["id"], root_page["title"])

    #     for path in page_key:
    #         self._make_pages(page_key, path)

    #     print("Finished directory making!")
    #     return page_list, page_key

    # def _make_pages(self, page_key: Dict[Path, Tuple[str, str]], path: Path) -> Dict[Path, Tuple[str, str]]:
    #     if not page_key[path] is None:
    #         return page_key

    #     if page_key[path.parent] is None:
    #         self._make_pages(page_key, path.parent)

    #     parent_id = page_key[path.parent][0]
    #     new_name = self.alias_name(path.name)
    #     new_page = self.make_confluence_page_directory(new_name, parent_id)
    #     page_key[path] = (new_page["id"], new_name)
    #     return page_key

    # def page_key_to_string(self, page_key: Dict[Path, Tuple[str, str]]) -> Dict[str, Tuple[str, str]]:
    #     new_page_key: Dict[str, Tuple[str, str]] = {}
    #     for page in page_key:
    #         page_path = str(page)
    #         new_page_key[page_path] = page_key[page]
    #     return new_page_key

    # def download_and_upload_resource(self, resource_names: Union[str, List[str]], page_id: str):
    #     if isinstance(resource_names, str):
    #         resource_names = [resource_names]

    #     temp_dir = Path(tempfile.mkdtemp())

    #     for name in resource_names:
    #         name = Path(name)
    #         filename = name.stem
    #         ext = name.suffix
    #         gridout = self.mongo_man.find_in_grid(grid_name=self.grid_name, filename=filename, extension=ext)
    #         temp_file = temp_dir / name
    #         with temp_file.open("wb") as f:
    #             f.write(gridout.read())
    #     print(f"Adding attachment {filename}{ext}")
    #     self.add_confluence_attachments(temp_dir, page_id)

    #     for item in os.listdir(temp_dir):
    #         (temp_dir / item).unlink()
    #     temp_dir.rmdir()

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

    # def get_mongo_page_blocks(self):
    #     return self.mongo_man.find_in_col(collection_name=self.collection_name, type=DocBlockElementType.PAGE.value)

    def get_confluence_page_id(self, title: str) -> str:
        return self.confluence_client.get_page_id(self.space_key, title)

    def make_confluence_page(self, title: str, content: str, parent_id: str) -> dict:
        new_title = self.alias_name(title)
        new_page = self.confluence_client.create_page(self.space_key, new_title, content, parent_id)
        print(f'''Created page, "{new_title}"''')
        return new_page

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
        print(f'''Created page, "{new_title}"''')
        return new_page

    def add_confluence_attachments(self, resource_dir: Union[Path, str], page_id: str):
        resource_dir = Path(resource_dir)
        for item in os.listdir(resource_dir):
            item_path = resource_dir / item
            self.confluence_client.attach_file(filename=item_path, page_id=page_id)
