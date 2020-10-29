

# ilia_ocr
Repository for the OCR team. Should contain (completed items in bold):
 * **Iverieli scraping and segmenting code**
 	 * **Iverieli downloader**
 	 * **Iverieli segmenter**
	 * **Text extractor for PDFs with text layers**
 * Dataloader code (both for the chars from Iverieli and from the provided dataset)
	 * Preprocessors
		 * Page
		 * Box
		 * Paragraph
		 * Line
		 * Word
		 * Symbol
	* Document to image:json pairs pipeline
 * Semi-supervised pipeline for labeling Iverieli chars
	 * **Tkiner-based GUI labeler**
	 * **Tkinter-based GUI corrector**
	 * FixMatch pipeline
 * Model TL/training code
 * Code for the FastAPI server serving the model
 * Script for wrapping up the Flask server in a docker container 
	 * Script for deploying the container to the server

## Informal FastAPI server description
Global namespace components:
* *upload\_service*: image conversion, preprocessing, and chararcter box detection service, queue.
* *extraction\_service*: service, queue for for extracting character boxes from the image files.
* *ocr\_service*: Inference service, queue.

Exposed API (not RESTful but close enough  ¯\\\_(ツ)\_/¯):
* Upload `POST /api/upload`
	* Places the file in the payload into *upload\_service* queue.
	* Payload: document to be uploaded
	* Returns: session key		
* Get conversion progress `GET /api/conversion_progress`
	* Returns the queue index/progress percentage of the uploaded file
	* Payload: session key
	* Returns: queue index/progress on the conversion/preprocessing/box detection of the uploaded file
* Get page boxes `GET /api/boxes_page`
	* Get the extracted box boundaries on a specific page
	* Payload: session key, page number
	* Returns: JSON with a list of 4-tuples (box boundaries)
* Submit box edits `POST /api/submit_edits`
	* Overwrite a page's box boundaries
	* Payload: session key, page number, JSON with a list of 4-tuples (box boundaries)
	* Returns: confirmation of successful edit
* Start box extraction `GET /api/extract`
	* Place the converted images and the boundary boxes into *extraction\_service*.
	* Payload: session key
	* Returns: confirmation on the start of extraction
* Get extraction progress `GET /api/extraction_progress`
	* Gets the session's index/progress in the box extraction queue.
	* Payload: session key
	* Returns: queue index/progress percentage on box extraction.
* Start inference `GET /api/ocr`
	* Places the extracted boxes in *ocr\_service*.
	* Payload: session key.
	* Returns: confirmation on the start of inference.
* Get inference progress `GET /api/ocr_progress`
	* Gets the session's index/progress in the inference queue.
	* Payload: session key
	* Returns: queue index/progress percentage on ocr.
* Download `GET /api/output`
	* Payload: session key
	* Returns: OCR results in plain text
	
Response examples can be found in [responses_example.txt](responses_example.txt).

	
## Iverieli examples
Good: 

<img src="resources/good1.png" width="50">
<img src="resources/good2.png" width="50">
<img src="resources/good3.png" width="50">

Bad:

<img src="resources/bad.png" width="200">
