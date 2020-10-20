
# ilia_ocr
Repository for the OCR team. Should contain (completed items in bold):
 * **Iverieli scraping and segmenting code**
 * Dataloader code (both for the chars from Iverieli and from the provided dataset)
 * Semi-supervised pipeline for labeling Iverieli chars
	 * Tkiner-based GUI labeler
	 * Classifier
 * Model TL/training code
 * Code for the Flask server serving the model
 * Script for wrapping up the Flask server in a docker container 
	 * Script for deploying the container to the server

## Informal Flask server description
Global namespace components:
* *upload\_service*: image conversion, preprocessing, and chararcter box detection service, queue.
* *extraction\_service*: service, queue for for extracting character boxes from the image files.
* *ocr\_service*: Inference service, queue.
* *overlay\_service*:  service and queue for overlaying OCR'd character back onto the images/PDF.

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
* Start overlay `GET /api/overlay`
	* Places the extracted boxes in *overlay\_service*.
	* Payload: session key.
	* Returns: confirmation on the start of inference.
* Get overlay progress `GET /api/overlay_progress`
 	* Gets the session's index/progress in the overlay queue.
	* Payload: session key
	* Returns: queue index/progress percentage on overlay.
* Download `GET /api/download`
	* Payload: session key, file type (plain text/PDF with overlay/image archive).
	* Returns: OCR'd file of the requested type.

## Iverieli examples
Good: 

<img src="resources/good1.png" width="50">
<img src="resources/good2.png" width="50">
<img src="resources/good3.png" width="50">

Bad:

<img src="resources/bad.png" width="200">
