# import module
import os
import shutil
import cv2
from pdf2image import convert_from_path

# Store Pdf with convert_from_path function
images = convert_from_path(input("Enter your pdfs path:"))
lessOrMore = input("Y/N Would you like to isolate PDFS below(Y) or above(N) the text percentage?")
if lessOrMore.upper() != "N" and lessOrMore.upper() != "Y":

    print("Please answer with Y or N.")
    exit()
percentageCap = input("What percentage text would you like to isolate?")
# Creates relevant folders if they don't already exist (for organization purposes)
if not os.path.exists('unprocessed'):
    os.makedirs('unprocessed')
if not os.path.exists('processed'):
    os.makedirs('processed')

for i in range(len(images)):
    # Save pages as images in the pdf
    images[i].save('unprocessed/page-' + str(i) + '.jpg', 'JPEG')
# Loop through every stored image for processing
for filename in os.listdir("unprocessed"):
    if filename.endswith(".jpg"):
        # Convert image to grayscale
        image = cv2.imread("unprocessed/" + filename)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 3)

        mask = thresh.copy()
        mask = cv2.merge([mask, mask, mask])
        # Remove undesirable contours (leave only text)
        picture_threshold = image.shape[0] * image.shape[1] * .05
        cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            area = cv2.contourArea(c)
            if area < picture_threshold:
                cv2.drawContours(mask, [c], -1, (0, 0, 0), -1)

        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        result = cv2.bitwise_xor(thresh, mask)
        # Now that all the text is isolated, all that is needed is to count the amount of white pixels on the screen
        # and turn that into a percentage
        text_pixels = cv2.countNonZero(result)
        percentage = (text_pixels / (image.shape[0] * image.shape[1])) * 100
        print("Page number:" + filename.split("-")[1].split(".")[0])
        print('Percentage: {:.2f}%'.format(percentage))
        if lessOrMore.upper() == "N":
            if percentage > float(percentageCap):
                filenum = filename.split("-")[1]
                shutil.move("unprocessed/page-" + str(filenum), "processed/page-" + str(filenum) )
        if lessOrMore.upper() == "Y":
            if percentage < float(percentageCap):
                filenum = filename.split("-")[1].split(".")[0]
                filenum = int(filenum) + i
                shutil.move("unprocessed/page-" + str(filenum), "processed/page-" + str(filenum))

        cv2.imshow('thresh', thresh)
        cv2.imshow('result', result)
        cv2.imshow('mask', mask)
