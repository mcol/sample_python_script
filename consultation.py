import pytesseract
import argparse
import os
import deep_translator
from wand.image import Image as WImage
from deep_translator import (GoogleTranslator)

## tesseract and googletranslator use different iso639 codes:
## tesseract: iso639-2t (3-letter codes)
## googletranslator: iso639-1 (2-letter codes)
## our script accepts 2-letter codes and uses the iso639 package to convert to 3-letter codes
from iso639 import Language as iso

pytesseract.tesseract_cmd = r"tesseract"

## command line arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help="path to the input image", default="{name}")
ap.add_argument("-l", "--lang", help="input language (2-character ISO 639-1 language codes, default: 'en')", default="en")
ap.add_argument("-t", "--to", type=str, help="translated language (2-charachter ISO 639-1 codes, default: 'en')", default="en")
ap.add_argument("-p", "--psm", type=int, help="Tesseract PSM mode", default=3)
args = vars(ap.parse_args())

# 2 letter language codes
from_lang = args["lang"]
to_lang = args["to"]

## 3-letter code of the translation language
tess_lang = iso.from_part1(from_lang).part2t

## options for pytesseract
tess_options = "-l {} --psm {}".format(tess_lang, args["psm"])

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
	translated=GoogleTranslator(source=from_lang, target=to_lang).translate(text)
	trans=str(translated)
	with open('translated_' + gray_name + '.txt', 'w', encoding='utf-8') as f:
		f.write(trans)
