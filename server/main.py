from fastapi import (
    FastAPI,
    BackgroundTasks,
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
import random
import string
import os
from urllib.parse import urlparse
from dataprocessor import convert_pdf, process_images
from middleware import LimitUploadSize

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str

if (disable_interactve_docs := os.getenv("DISABLE_INTERACTIVE_DOCS", None)) is None:
    app = FastAPI(title="ilia_ocr API", description="API for OCRing Georgian-language documents")
else:
    app = FastAPI(title="ilia_ocr API", description="API for OCRing Georgian-language documents", docs_url="/documentation", redoc_url=None)
app.add_middleware(LimitUploadSize, max_upload_size=os.getenv("MAX_UPLOAD_SIZE", 1_000_000_000))  # ~1GB



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


ids = []
documents = []
delete_key_store = {}
image_types = ["image/jpeg", "image/png"]
files_path = os.getenv("OCR_STATIC_FILES_DIRECTORY", "./files")
app.mount("/files", StaticFiles(directory=files_path), name="files")


class Page(BaseModel):
    url: str
    page: int
    text: str
    progress: Tuple[str, float]


class Document(BaseModel):
    id: str
    pages: List[Page]


@app.post("/api/documents", status_code=201)
async def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
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
            convert_pdf(await files[0].read(), f"{files_path}/{new_id}/")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not convert PDF. (Invalid PDF?)")
    elif not all([f.content_type in f.content_type for f in files]):
        raise HTTPException(
            status_code=400,
            detail="Uploaded files must be JPEG or PNG images, or a single PDF.",
        )
    img_files = os.listdir(f"{files_path}/{new_id}/")
    pages = []
    for i, img_file in enumerate(img_files):
        url = base_url + "/files/" + img_file
        page = i
        text = ""
        progress = ("Starting processing", 0.0)
        pages.append(Page(url=url, page=page, text=text, progress=progress))
    new_document = Document(id=new_id, pages=pages)
    documents.append(new_document)
    delete_key = get_random_string(10)
    delete_key_store[new_id] = delete_key
    background_tasks.add_task(process_images, f"{files_path}/{new_id}/", new_document, use_erosion, latin_mode)
    return {
        "location": base_url + "/api/documents/" + new_id + "?page=0",
        "delete_key": delete_key,
    }


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str, delete_key: str):
    doc = [d for d in documents if d.id == document_id]
    if len(d) == 0:
        raise HTTPException(status_code=404, detail=f"Document with id {document_id} not found.")
    if delete_key_store[document_id] != delete_key:
        raise HTTPException(
            status_code=403,
            detail=f"delete_key {delete_key} incorrent for document with id {document_id}.",
        )
    ids.remove(document_id)
    delete_key_store.pop(document_id)
    documents.remove(doc[0])


@app.get("/api/documents/{document_id}")
async def get_document(response: Response, document_id: str, page: int = Query(-1, ge=0)):
    doc = [d for d in documents if d.id == document_id]
    if len(doc) == 0:
        raise HTTPException(status_code=404, detail=f"Document with id {document_id} not found.")
    doc = doc[0]
    if page >= len(doc.pages):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot get page {page} of document {document_id} with {len(doc.pages)} pages.",
        )
    if page == -1:
        if not all([p.progress[0] == "Ready" for p in doc.pages]):
            response.status_code = 202
        return doc.pages
    if doc.pages[page].progress[0] != "Ready":
        response.status_code = 202
    return doc.pages[page]


@app.get("/api/")
async def read_root(request: Request):
    return {"documents": {"href": "/api/documents"}}


@app.get("/api/documents")
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
