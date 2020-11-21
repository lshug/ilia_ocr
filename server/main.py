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
from typing import List, Dict, Tuple, Optional
import math
import os
import shutil
from urllib.parse import urlparse
from .data_processor import convert_pdf, process_images
from .server_utils import (
    LimitUploadSize, 
    get_random_string, 
    run_in_thread, 
)
from .models import (
    Page, 
    Document,
    new_document_id, 
    all_documents,
    retrieve_document,
    retrieve_page,
)


title = "ilia_ocr API"
description = "API for OCRing Georgian-language documents"
tags_metadata = [
    {"name": "essential", "description": "Essential OCR service endpoinds, unit-tested."},
    {"name": "non-essential", "description": "Non-essential endpoints, not unit-tested."},
]

if (disable_interactve_docs := os.getenv("DISABLE_INTERACTIVE_DOCS", None)) is None:
    app = FastAPI(title=title, description=description, openapi_tags=tags_metadata)
else:
    app = FastAPI(title=title, description=description, openapi_tags=tags_metadata, docs_url=None, redoc_url=None)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

if (domain_name := os.getenv("FRONTEND_DOMAIN_NAME", None)) is not None:
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
app.add_middleware(LimitUploadSize, max_upload_size=os.getenv("MAX_UPLOAD_SIZE", 1_000_000_000))  # ~1GB

image_types = ["image/jpeg", "image/png"]
files_path = os.getenv("OCR_STATIC_FILES_DIRECTORY", f"{os.path.dirname(__file__)}/files/")
if not os.path.isdir(files_path):
    os.mkdir(files_path)
ids = os.listdir(files_path)
app.mount("/files", StaticFiles(directory=files_path), name="files")


@app.post("/api/documents", status_code=201, tags=["essential"])
def upload_document(request: Request, files: List[UploadFile] = File(...), use_erosion: bool = False, latin_mode: bool = False):
    o = urlparse(str(request.url))
    base_url = o.scheme + "://" + o.netloc
    new_id = new_document_id()
    if not all([f.content_type in image_types for f in files]):
        raise HTTPException(status_code=400, detail="Uploaded files must be JPEG or PNG images.")
    else:
        os.mkdir(f"{files_path}/{new_id}")
        for i,f in enumerate(files):
            contents = f.file.read()
            open(f"{files_path}/{new_id}/{i}_{f.filename}",'wb').write(contents)
    img_files = sorted(os.listdir(f"{files_path}/{new_id}/"))
    pages = []
    for i, img_file in enumerate(img_files):
        id = new_id + str(i)
        url = base_url + "/files/" + new_id + '/' + img_file
        page = i
        text = ""
        progress = ("Starting processing", 0.0)
        pages.append(Page(id=id, url=url, page=page, text=text, progress=progress))
    new_document = Document(id=new_id, pages=[p.id for p in pages])
    run_in_thread(process_images, f"{files_path}/{new_id}/", new_document, use_erosion, latin_mode)
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
    return retrieve_page(page)


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
