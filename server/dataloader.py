import os

def process_pdf(path):
    #extract images
    #delete delete pdf
    #run process_images
    pass

def process_images(path):
    #for each image:
    #   Run full tesseract symbol level
    #   Run symbol-level boxes through erosion check
    #   Run tesseract layout analsis on above levels
    #   Remove labels for everything that's not punctuation
    #   Make the full document hierarchy json by checking boundaries.
    #List of (img,json)
