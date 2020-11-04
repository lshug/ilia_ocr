from fastapi.testclient import TestClient
from main import app, ids, documents, delete_key_store, Document, Page
from server_utils import get_random_string
import tempfile
import os

client = TestClient(app)

temp_doc_id, temp_doc_delete_key = None, None


def create_temp_doc(complete=0, incomplete=10):
    global temp_doc_id
    global temp_doc_delete_key
    files_path = os.getenv("OCR_STATIC_FILES_DIRECTORY", "./files/")
    pages = []
    for i in range(incomplete):
        url = 'ignore'
        page = i
        text = ""
        progress = ("Starting processing", 0.0)
        pages.append(Page(url=url, page=page, text=text, progress=progress))
    for j in range(incomplete, incomplete+complete):
        url = 'ignore'
        page = j
        text = ""
        progress = ("Ready", 1.0)
        pages.append(Page(url=url, page=page, text=text, progress=progress))
    new_id = get_random_string(10)
    new_document = Document(id=new_id, pages=pages)
    documents.append(new_document)
    ids.append(new_id)
    os.mkdir(f"{files_path}/{new_id}")
    delete_key = get_random_string(10)
    delete_key_store[new_id] = delete_key
    temp_doc_id = new_id
    temp_doc_delete_key = delete_key


# POST /api/documents


def test_noncompatible_file_type_upload():
    response = client.post("/api/documents", files={"files": ("filename", open('test_resources/bad_file.bad', "rb"), "bad/bad")})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Uploaded files must be JPEG or PNG images, or a single PDF.'}
    
def test_incompatible_image_types_upload():
    response = client.post("/api/documents", files={"files": ("filename", open('test_resources/image1.gif', "rb"), "image/gif")})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Uploaded files must be JPEG or PNG images, or a single PDF.'}

def test_no_file_upload():
    response = client.post("/api/documents")
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'files'], 'msg': 'field required', 'type': 'value_error.missing'}]}

def test_invalid_pdf_upload():
    response = client.post("/api/documents", files={"files": ("filename", open('test_resources/bad_pdf.pdf', "rb"), "application/pdf")})
    assert response.status_code == 500
    assert response.json() == {'detail': "Could not convert PDF. (Invalid PDF?)"}

def test_content_length_over_max():
    max_size = os.getenv("MAX_UPLOAD_SIZE", 1_000_000_000)
    f = tempfile.TemporaryFile(suffix='.pdf')
    f.write(b'a')
    f.seek(max_size+1)
    f.write(b'b')
    f.seek(0)
    response = client.post("/api/documents", files={"files": ("filename", f, "application/pdf")})
    assert response.status_code == 413

def test_pdf_upload_fail():
    files_path = os.getenv("OCR_STATIC_FILES_DIRECTORY", "./files/")
    response = client.post("/api/documents", files={"files": ("filename", open('test_resources/pdf.pdf', "rb"), "application/pdf")})
    assert response.status_code == 201
    assert os.path.isdir(f'{files_path}/{response.json()["id"]}')

def test_images_upload_error():
    files_path = os.getenv("OCR_STATIC_FILES_DIRECTORY", "./files/")
    files = [('files', ('f1',open('test_resources/image1.png', "rb"),'image/jpeg')),('files', ('f2',open('test_resources/image1.png', "rb"),'image/jpeg'))]
    response = client.post("/api/documents", files=files)
    assert response.status_code == 201
    assert os.path.isdir(f'{files_path}/{response.json()["id"]}')

def test_upload_high_load_fail():
    files_path = os.getenv("OCR_STATIC_FILES_DIRECTORY", "./files/")
    for i in range(1000):
        files = [('files', ('f1',open('test_resources/image1.png', "rb"),'image/jpeg')),('files', ('f2',open('test_resources/image1.png', "rb"),'image/jpeg'))]
        response = client.post("/api/documents", files=files)
        assert response.status_code == 201
        assert os.path.isdir(f'{files_path}/{response.json()["id"]}')

# GET /api/documents/item?page


def test_get_nonexisting_item():
    response = client.get("/api/documents/non_existing")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Document with id non_existing not found.'}

def test_get_out_of_bounds_page():
    create_temp_doc(10,0)
    response = client.get("/api/documents/"+temp_doc_id+'?page=10')
    assert response.status_code == 400
    
def test_incomplete_page_wrong_code():
    create_temp_doc(5,5)
    response1 = client.get("/api/documents/"+temp_doc_id+'?page=0')
    response2 = client.get("/api/documents/"+temp_doc_id+'?page=5')
    assert response1.status_code == 202
    assert response2.status_code == 200

def test_all_incomplete_no_202():
    create_temp_doc()
    response = client.get("/api/documents/"+temp_doc_id)
    assert response.status_code == 202


def test_all_complete_no_200():
    create_temp_doc(10,0)
    response = client.get("/api/documents/"+temp_doc_id)
    assert response.status_code == 200



# DELETE /api/documents/item


def test_delete_non_existing_id():
    response = client.delete("/api/documents/non_existing?delete_key=test")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Document with id non_existing not found.'}

def test_delete_wrong_key():
    create_temp_doc()
    response = client.delete(f"/api/documents/{temp_doc_id}?delete_key=test")
    assert response.status_code == 403

def test_delete_fail():
    files_path = os.getenv("OCR_STATIC_FILES_DIRECTORY", "./files/")
    create_temp_doc()
    response = client.delete(f"/api/documents/{temp_doc_id}?delete_key={temp_doc_delete_key}")
    assert response.status_code == 200
    assert not os.path.isdir(f'{files_path}/{temp_doc_id}')
    
