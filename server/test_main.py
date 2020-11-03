from fastapi.testclient import TestClient
from main import app, ids, documents, delete_key_store

client = TestClient(app)

temp_doc_id, temp_doc_delete_key = None

def create_temp_doc():
    pass

def create_partionally_complete_temp_doc():
    pass

def complete_temp_doc():
    pass

#POST /api/documents

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

#GET /api/documents/item?page

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

#DELETE /api/documents/item

def test_delete_non_existing_id():
    pass

def delete_wrong_key():
    pass

def delete_fail():
    pass
