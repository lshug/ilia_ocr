import json
from pydantic import BaseModel
from typing import List, Dict, Tuple, Optional
from .server_utils import redis_session, get_random_string

class Page(BaseModel): # on init, update list in redis on setattr, update redis
    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)
        redis_session.lpush('pages', self.id)
        redis_session.set('pages/' + self.id, self.json())
    def __setattr__(self, name, value):
        super(Page, self).__setattr__(name, value)
        redis_session.set('pages/' + str(self.id), self.json())
    id: str
    url: str
    page: int
    text: str
    progress: Tuple[str, float]


class Document(BaseModel): # on init, update list in redis.
    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        redis_session.set('documents/' + self.id, self.json())
    id: str
    pages: List[str] 

def retrieve_document(id):
    return Document.parse_raw(redis_session.get('documents/' + id).decode('utf8'))

def all_documents():
    try:
        ids = json.loads(redis_session.get('documents').decode('utf8'))
    except:
        return []
    return [retrieve_document(id) for id in ids]

def retrieve_page(id):
    return Page.parse_raw(redis_session.get('pages/' + id).decode('utf8'))

def new_document_id():
    while (new_id := get_random_string(10)) in [x.decode() for x in redis_session.lrange('documents', 0, -1)]:
        new_id = get_random_string(10)
    redis_session.lpush('documents', new_id)
    return new_id
