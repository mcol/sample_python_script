import pytesseract
import argparse
import os
import deep_translator
from wand.image import Image as WImage
from deep_translator import (GoogleTranslator)

pytesseract.tesseract_cmd = r"tesseract"

## command line arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help="path to the input image", default='{name}')
ap.add_argument("-l", "--lang", help='path to the language', default='eng')
ap.add_argument("-t", "--to", type=str, default="en", help="eng")
ap.add_argument("-p", "--psm", type=int, default=3, help="Tesseract PSM mode")
args = vars(ap.parse_args())

## options for pytesseract
tess_options = "-l {} --psm {}".format(args["lang"], args["psm"])

## image to process
item = args["image"]
print("Processing image {}".format(item))

gray_name = 'gray_' + item

with WImage(filename=item) as img:

	## Transform image from color to grayscale
	img.transform_colorspace('gray')
	img.adaptive_threshold(width=16, height=16, offset=-0.15 * img.quantum_range)
	img.save(filename=gray_name)

	## Extract the text
	text = pytesseract.image_to_string(gray_name, config=tess_options)

	## Write-up original text
	outfile = open(gray_name + '.txt', 'w', encoding='utf-8')
	outfile.write(text)

	## Write-up translated text
	translated=GoogleTranslator(source='auto', target=args["to"]).translate(text)
	trans=str(translated)
	with open('translated_' + gray_name + '.txt', 'w', encoding='utf-8') as f:
		f.write(trans)
