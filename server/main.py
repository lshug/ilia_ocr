from fastapi import (
    FastAPI,
    Request,
    Response,
    Query,
    Path,
    File,
    UploadFile,
    HTTPException,
    status,
)
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import math
from urllib.parse import urlparse
from .server_utils import celery_app
from .server_utils import (
    LimitUploadSize,
    start_redis_celery,
)
from .models import (
    Page, 
    Document,
    DocumentPutRequest,
    new_document_id, 
    all_documents,
    retrieve_document,
    retrieve_page,
    insert_raw_file,
    insert_test_image,
    connect_db,
)
from .settings import settings

start_redis_celery()

title = "ilia_ocr API"
description = "API for OCRing Georgian-language documents"
tags_metadata = [
    {"name": "essential", "description": "Essential OCR service endpoinds, unit-tested."},
    {"name": "non-essential", "description": "Non-essential endpoints, not unit-tested."},
]

if settings.disable_interactve_docs is False:
    app = FastAPI(title=title, description=description, openapi_tags=tags_metadata)
else:
    app = FastAPI(title=title, description=description, openapi_tags=tags_metadata, docs_url=None, redoc_url=None)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

if (domain_name := settings.domain_name) is not None:
    origins.append(f"http://{domain_name}")
    origins.append(f"http://{domain_name}:8080")
    origins.append(f"https://{domain_name}")
    origins.append(f"https://{domain_name}:8080")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LimitUploadSize, max_upload_size=settings.max_upload_size)

@app.on_event("startup")
async def startup_event():
    await connect_db()
    await insert_test_image()

async def process_files(files):
    if not all([f.content_type in ["image/jpeg", "image/png"] for f in files]):
        raise HTTPException(status_code=400, detail="Uploaded files must be JPEG or PNG images.")
    ids = [await insert_raw_file(f.filename, f.content_type, await f.read()) for f in files]
    return ids
    
async def process_file_ids(file_ids, new_id, use_erosion, callback_url):
    progress = ("Starting processing", 0.0)
    pages = [Page(id=new_id+str(i), page=i, text="", progress=progress) for i in range(len(file_ids))]
    new_document = Document(id=new_id, pages=[p.id for p in pages])
    celery_app.send_task('process_images', args=[new_id, file_ids, new_document.pages, use_erosion, callback_url])

@app.post("/api/documents", status_code=201, tags=["essential"])
async def process_document(request: Request, request_body: DocumentPutRequest, use_erosion: bool = False):
    file_ids, callback_url = request_body.file_ids, request_body.callback_url
    if len(file_ids) == 0:
        raise HTTPException(status_code=400, detail="No file ids provided.")
    o = urlparse(str(request.url))
    base_url = o.scheme + "://" + o.netloc
    new_id = new_document_id()
    await process_file_ids(file_ids, new_id, use_erosion, callback_url)
    return {
        "id" : new_id,
        "location" : base_url + "/api/documents/" + new_id,
        "first_page_location": base_url + "/api/documents/" + new_id + "?page=0"
    }


@app.get("/api/", tags=["non-essential"])
async def read_api(request: Request):
    return {"documents": {"href": "/api/documents"}}

@app.get("/", tags=["non-essential"])
async def read_root(request: Request):
    return {"api": {"href": "/api/"}}


@app.get("/api/documents/{document_id}", tags=["essential"])
async def get_document(response: Response, document_id: str, page: int = Query(None, ge=0)):
    try:
        doc = retrieve_document(document_id)
    except:
        raise HTTPException(status_code=404, detail=f"Document with id {document_id} not found.")
    if page is not None and page >= len(doc.pages):
        raise HTTPException(status_code=400, detail=f"Cannot get page {page} of document {document_id} with {len(doc.pages)} pages.")
    if page == None:
        pages = [retrieve_page(p) for p in doc.pages]
        if not all([p.progress[0] == "Ready" for p in pages]):
            response.status_code = 202
        return pages
    if doc.pages[page].progress[0] != "Ready":
        response.status_code = 202
    return retrieve_page(doc.pages[page])


@app.get("/api/documents", tags=["non-essential"])
async def list_documents(page: int = Query(0, ge=0), per_page: int = Query(20, ge=1, le=2000)):
    documents = all_documents()
    base_str = "/api/documents?page={}&per_page=" + str(per_page)
    results = documents[per_page * page : per_page * (page + 1)]
    self_url = base_str.format(page)
    first_url = base_str.format(0)
    previous_url = "" if page == 0 else base_str.format(page - 1)
    next_url = "" if page == len(documents) // per_page else base_str.format(page + 1)
    last_url = base_str.format(len(documents) // per_page)
    links = {
        "self": self_url,
        "first": first_url,
        "previous": previous_url,
        "next": next_url,
        "last": last_url,
    }
    metadata = {
        "page": page,
        "per_page": per_page,
        "page_count": math.ceil(len(documents) / per_page),
        "total_count": len(documents),
        "links": links,
    }
    return {"_metadata": metadata, "records": results}

@app.post("/api/documents/fileupload", status_code=201, tags=["non-essential"])
async def upload_files(request: Request, files: List[UploadFile] = File(None)):
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="No files provided.")
    file_ids = await process_files(files)
    return {
        "file_ids" : file_ids
    }
