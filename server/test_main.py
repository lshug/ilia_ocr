from fastapi.testclient import TestClient
from main import app, ids, documents, delete_key_store, Document, Page
from server_utils import get_random_string

client = TestClient(app)

temp_doc_id, temp_doc_delete_key = None


def create_temp_doc(complete=0, incomplete=10):
    pages = []
    for i in range(incomplete):
        url = 'ignore'
        page = i
        text = ""
        progress = ("Starting processing", 0.0)
        pages.append(Page(url=url, page=page, text=text, progress=progress))
    for j in range(i+1, i+complete):
        url = 'ignore'
        page = j
        text = ""
        progress = ("Ready", 1.0)
        pages.append(Page(url=url, page=page, text=text, progress=progress))
    new_id = get_random_string(10)
    documents.append(new_document)
    delete_key = get_random_string(10)
    delete_key_store[new_id] = delete_key
    temp_doc_id = new_id
    temp_doc_delete_key = delete_key


# POST /api/documents


def test_noncompatible_file_type_upload():
    pass


def test_no_file_upload():
    pass


def test_invalid_pdf_upload():
    pass


def test_incompatible_image_types_upload():
    pass


def test_pdf_no_content_length_header():
    pass


def test_images_no_content_length_header():
    pass


def test_pdf_invalid_content_length_header():
    pass


def test_images_invalid_content_length_header():
    pass


def test_pdf_content_length_over_max():
    pass


def test_images_content_length_over_max():
    pass


def test_pdf_ok_folder_not_created():
    pass


def test_images_ok_folder_not_created():
    pass


# GET /api/documents/item?page


def test_get_nonexisting_item():
    pass


def test_get_existing_item_fails():
    pass


def test_get_negative_page():
    pass


def test_get_out_of_bounds_page():
    pass


def test_incomplete_page_no_202():
    pass


def test_complete_page_no_200():
    pass


def test_all_incomplete_no_202():
    pass


def test_all_complete_no_200():
    pass


def test_provided_url_inaccessible():
    pass


# DELETE /api/documents/item


def test_delete_non_existing_id():
    pass


def delete_wrong_key():
    pass

