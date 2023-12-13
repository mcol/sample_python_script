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
ap.add_argument("-p", "--psm 3", type=int, default=13, help="Tesseract PSM mode")
args = vars(ap.parse_args())

## options for pytesseract
options = "-l {} --psm 3 {}".format(args["lang"], args["psm 3"])

## image to process
item = args["image"]
print("Processing image {}".format(item))

with WImage(filename=item) as img:

	## Transform image from color to grayscale
	img.transform_colorspace('gray')
	img.adaptive_threshold(width=16, height=16, offset=-0.15 * img.quantum_range)
	img.save(filename='gray_'+item)

	## Extract the text
	name='gray_'+item
	text = pytesseract.image_to_string(name)

	## Write-up original text
	outfile = open('gray_'+item+'.txt', 'w', encoding='utf-8')
	outfile.write(text)

	## Write-up translated text
	translated=GoogleTranslator(source='auto', target=args["to"]).translate(text)
	trans=str(translated)
	with open('gray_translated_'+item+'.txt', 'w', encoding='utf-8') as f:
		f.write(trans)
