## Script to extract text from an image and optionally to translate it into a second
## language.
##
## It requires Google's Tesseract-OCR Engine to be installed on the system.
## The path to the tesseract executable can be specified through the
## `pytesseract.pytesseract.tesseract_cmd` setting below, if it is not in the PATH.

import os
import sys
import pytesseract
from argparse import ArgumentParser as ArgParser
from wand.image import Image as WImage
from deep_translator import GoogleTranslator

## tesseract and googletranslator use different iso639 codes:
## tesseract: iso639-2t (3-letter codes)
## googletranslator: iso639-1 (2-letter codes)
## our script accepts 2-letter codes and uses the iso639 package to convert to 3-letter codes
from iso639 import Language as iso

## change the following if the tesseract binary is not in the PATH
pytesseract.pytesseract.tesseract_cmd = r"tesseract"

def main(item, from_lang="en", to_lang="en", psm=3):

	## 3-letter code of the translation language
	tess_lang = iso.from_part1(from_lang).part2t

	## is translation required?
	translate = True if from_lang != to_lang else False

	## options for pytesseract
	tess_options = "-l {} --psm {}".format(tess_lang, psm)

	## image to process
	if not os.path.exists(item):
		raise FileNotFoundError

	## temporary grayscale image
	gray_item = 'gray_' + item

	## extensionless filename
	item_filename = item.rsplit('.',1)[0]

	with WImage(filename=item) as img:

		## Transform image from color to grayscale
		img.transform_colorspace('gray')
		img.adaptive_threshold(width=16, height=16, offset=0.15 * img.quantum_range)
		img.save(filename=gray_item)

		## Extract the text
		text = pytesseract.image_to_string(gray_item, config=tess_options)

		## Remove the grayscale image
		os.remove(gray_item)

		## Write-up original text
		with open(item_filename + '_orig.txt', 'w', encoding='utf-8') as outfile:
			outfile.write(text)

		if translate:
			## Write-up translated text
			trans = GoogleTranslator(source=from_lang, target=to_lang).translate(text)
			with open(item_filename + '_trans_' + to_lang + '.txt', 'w', encoding='utf-8') as f:
				f.write(trans)


if __name__ == '__main__':
	## define the command line arguments
	ap = ArgParser(description="Extract text from an image and optionally translate it to a second language")
	ap.add_argument("image", help="path to the input image")
	ap.add_argument("-l", "--lang", help="input language (2-character ISO 639-1 language codes, default: 'en')", default="en")
	ap.add_argument("-t", "--to", type=str, help="translated language (2-charachter ISO 639-1 codes, default: 'en')", default="en")
	ap.add_argument("-p", "--psm", type=int, help="Tesseract PSM mode", default=3)

	## parse the command line arguments
	args = vars(ap.parse_args())
	image = args["image"]
	from_lang = args["lang"]
	to_lang = args["to"]
	psm = args["psm"]

	try:
		main(image, from_lang, to_lang, psm)
		print("Processed image {}".format(image))
	except FileNotFoundError:
		print("Skipping non-existing file {}".format(image), file=sys.stderr)
	except Exception as e:
		print("Failed processing file {}, reason: {}".format(image, e.__class__.__name__), file=sys.stderr)
