

# ilia_ocr
Repository for the OCR team. Should contain (completed items in bold):
 * **Iverieli scraping and segmenting code**
 	 * **Iverieli downloader**
 	 * **Iverieli segmenter**
	 * **Text extractor for PDFs with text layers**
 * **Semi-supervised pipeline for labeling Iverieli chars**
	 * **Tkiner-based GUI labeler**
	 * **Tkinter-based GUI corrector**
	 * **Model training and keras model generation code**
 * Server
    * **Dataloader code**
        * **Symbol heuristics**
            * **Erosion and resegmentation on wide symbols**
            * **Insert Tesseract-detected punctuations**
        * **Document to image:json pairs pipeline**
    * **FastAPI microservice**
    * **Model serving**
    * Unit tests
 * Script for wrapping up the Flask server in a docker container 
	 * Script for deploying the container to the server
