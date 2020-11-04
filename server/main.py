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
from pydantic import BaseModel
from typing import List, Dict, Tuple, Optional
import math
import os
import shutil
from urllib.parse import urlparse
from .data_processor import convert_pdf, process_images
from .server_utils import LimitUploadSize, get_random_string, run_in_thread


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

documents = []
delete_key_store = {}
image_types = ["image/jpeg", "image/png"]
files_path = os.getenv("OCR_STATIC_FILES_DIRECTORY", "./files/")
if not os.path.isdir(files_path):
    os.mkdir(files_path)
ids = os.listdir(files_path)
app.mount("/files", StaticFiles(directory=files_path), name="files")


class Page(BaseModel):
    url: str
    page: int
    text: str
    progress: Tuple[str, float]


class Document(BaseModel):
    id: str
    pages: List[Page]


@app.post("/api/documents", status_code=201, tags=["essential"])
def upload_document(
    request: Request,
    files: List[UploadFile] = File(...),
    use_erosion: bool = False,
    latin_mode: bool = False,
):
    o = urlparse(str(request.url))
    base_url = o.scheme + "://" + o.netloc
    while (new_id := get_random_string(10)) in ids:
        new_id = get_random_string(10)
    ids.append(new_id)
    pdf_converted = False
    if len(files) == 1 and files[0].content_type == "application/pdf":
        os.mkdir(f"{files_path}/{new_id}")
        try:
            convert_pdf(files[0].file.read(), f"{files_path}/{new_id}/")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not convert PDF. (Invalid PDF?)")
    elif not all([f.content_type in image_types for f in files]):
        raise HTTPException(
            status_code=400,
            detail="Uploaded files must be JPEG or PNG images, or a single PDF.",
        )
    else:
        os.mkdir(f"{files_path}/{new_id}")
        for f in files:
            contents = f.file.read()
            open(f"{files_path}/{new_id}/{f.filename}",'wb').write(contents)
    img_files = os.listdir(f"{files_path}/{new_id}/")
    pages = []
    for i, img_file in enumerate(img_files):
        url = base_url + "/files/" + new_id + '/' + img_file
        page = i
        text = ""
        progress = ("Starting processing", 0.0)
        pages.append(Page(url=url, page=page, text=text, progress=progress))
    new_document = Document(id=new_id, pages=pages)
    documents.append(new_document)
    delete_key = get_random_string(10)
    delete_key_store[new_id] = delete_key
    run_in_thread(process_images, f"{files_path}/{new_id}/", new_document, use_erosion, latin_mode)
    return {
        "id" : new_id,
        "location" : base_url + "/api/documents/" + new_id,
        "first_page_location": base_url + "/api/documents/" + new_id + "?page=0",
        "delete_key": delete_key,
    }


@app.get("/api/", tags=["non-essential"])
async def read_root(request: Request):
    return {"documents": {"href": "/api/documents"}}

@app.get("/", tags=["non-essential"])
async def read_root(request: Request):
    return {"api": {"href": "/api/"}}



@app.delete("/api/documents/{document_id}", tags=["essential"])
async def delete_document(document_id: str, delete_key: str):
    doc = [d for d in documents if d.id == document_id]
    if len(doc) == 0:
        raise HTTPException(status_code=404, detail=f"Document with id {document_id} not found.")
    if delete_key_store[document_id] != delete_key:
        raise HTTPException(
            status_code=403,
            detail=f"delete_key {delete_key} incorrent for document with id {document_id}.",
        )
    ids.remove(document_id)
    delete_key_store.pop(document_id)
    shutil.rmtree(f"{files_path}/{document_id}/")
    documents.remove(doc[0])


@app.get("/api/documents/{document_id}", tags=["essential"])
async def get_document(response: Response, document_id: str, page: int = Query(None, ge=0)):
    doc = [d for d in documents if d.id == document_id]
    if len(doc) == 0:
        raise HTTPException(status_code=404, detail=f"Document with id {document_id} not found.")
    doc = doc[0]
    if page is not None and page >= len(doc.pages):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot get page {page} of document {document_id} with {len(doc.pages)} pages.",
        )
    if page == None:
        if not all([p.progress[0] == "Ready" for p in doc.pages]):
            response.status_code = 202
        return doc.pages
    if doc.pages[page].progress[0] != "Ready":
        response.status_code = 202
    return doc.pages[page]


@app.get("/api/documents", tags=["non-essential"])
async def list_documents(page: int = Query(0, ge=0), per_page: int = Query(20, ge=1, le=2000)):
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
