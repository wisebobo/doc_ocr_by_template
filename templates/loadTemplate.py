# -*- coding:utf-8 -*-
import json
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
from operator import itemgetter


def imgEnhance(image, sharpness=1, contrast=1, brightness=1, medianFilter=3, autocontrast=True):

    if sharpness:
        image = ImageEnhance.Sharpness(image).enhance(sharpness)

    if contrast:
        image = ImageEnhance.Contrast(image).enhance(contrast)

    if brightness:
        image = ImageEnhance.Brightness(image).enhance(brightness)

    if medianFilter:
        image = image.filter(ImageFilter.MedianFilter(medianFilter))

    if autocontrast:
        image = ImageOps.autocontrast(image)

    return image

class ocrTemplate(object):

    def __init__(self, jsonFile, docType):
        self.jsonFile = jsonFile
        self.docType = docType
        self._width = 1000
        self._height = 700

        self.refBoxes, self.recogBoxes = self.load()


    def load(self):
        with open(self.jsonFile, 'r', encoding='utf-8') as fp:

            refBoxes = []
            recogBoxes = []

            try:
                _templates = json.load(fp)

                for i in range(len(_templates['templates'])):
                    doc_template = _templates['templates'][i]

                    if doc_template['templateId'] == self.docType:
                        for box in doc_template['referenceArea']:
                            refBoxes.append([int(box['x']), int(box['y']), int(box['width']), int(box['height']), box['keyword']])

                        for box in doc_template['recognitionArea']:
                            recogBoxes.append([int(box['x']), int(box['y']), int(box['width']), int(box['height']), box['fieldName'], box['type']])

                        refBoxes = sorted(refBoxes, key=itemgetter(1, 0))
                        recogBoxes = sorted(recogBoxes, key=itemgetter(1, 0))

                        break

            except Exception as e:
                print(e)
            finally:
                return refBoxes, recogBoxes


    def recog(self, img, ocrBoxes):
        refCnt = 0
        ratioBoxes = []
        newRecogBoxes = []

        for refBox in self.refBoxes:
            isFound = False
            for ocrBox in ocrBoxes:
                refValue = refBox[4].upper()
                ocrValue = ocrBox[4].upper()

                if refValue == ocrValue:
                    isFound = True
                else:
                    matchCnt = 0
                    refArray = refValue.split(' ')
                    for char in refArray:
                        if char in ocrValue:
                            matchCnt += 1

                    if matchCnt >= len(refArray) * 0.7:
                        isFound = True

                if isFound:
                    ratioBoxes.append([refBox[0], refBox[1], refBox[0] + refBox[2], refBox[1] + refBox[3], ocrBox[0], ocrBox[1], ocrBox[0] + ocrBox[2], ocrBox[1] + ocrBox[3]])
                    break

        if ratioBoxes:
            ratioBoxes_x = sorted(ratioBoxes, key=itemgetter(0,))
            ratioBoxes_y = sorted(ratioBoxes, key=itemgetter(1,))

            minRefX1 = ratioBoxes_x[0][0]
            maxRefX1 = ratioBoxes_x[-1][0]
            minOcrX1 = ratioBoxes_x[0][4]
            maxOcrX1 = ratioBoxes_x[-1][4]

            minRefX2 = ratioBoxes_x[0][2]
            maxRefX2 = ratioBoxes_x[-1][2]
            minOcrX2 = ratioBoxes_x[0][6]
            maxOcrX2 = ratioBoxes_x[-1][6]

            minRefY1 = ratioBoxes_y[0][1]
            maxRefY1 = ratioBoxes_y[-1][1]
            minOcrY1 = ratioBoxes_y[0][5]
            maxOcrY1 = ratioBoxes_y[-1][5]

            minRefY2 = ratioBoxes_y[0][3]
            maxRefY2 = ratioBoxes_y[-1][3]
            minOcrY2 = ratioBoxes_y[0][7]
            maxOcrY2 = ratioBoxes_y[-1][7]

            # if maxOcrX1 - minOcrX1 < 10 or maxRefX1 - minRefX1 < 10:
            #     ratioX1 = 1
            # else:
            ratioX1 = (maxOcrX1 - minOcrX1 + 1) / (maxRefX1 - minRefX1 + 1)

            # if maxOcrY1 - minOcrY1 < 10 or maxRefY1 - minRefY1 < 10:
            #     ratioY1 = 1
            # else:
            ratioY1 = (maxOcrY1 - minOcrY1 + 1) / (maxRefY1 - minRefY1 + 1)

            newImg = Image.new('RGB', (self._width, self._height))

            last_y = 0

            for recogBox in self.recogBoxes:
                calcX1 = int(abs(maxOcrX1 - (maxRefX1 - recogBox[0]) * ratioX1))
                calcY1 = int(abs(maxOcrY1 - (maxRefY1 - recogBox[1]) * ratioY1))
                calcX2 = int(recogBox[2] * ratioX1) + calcX1
                calcY2 = int(recogBox[3] * ratioY1) + calcY1

                # print('\n', recogBox[0], recogBox[1], recogBox[0] + recogBox[2], recogBox[1] + recogBox[3], calcX1, calcY1, calcX2, calcY2)

                cropped = img.crop((calcX1, calcY1, calcX2, calcY2))
                newImg.paste(cropped, (0, last_y))

                newRecogBoxes.append([0, last_y - 5, calcX2 - calcX1, calcY2 - calcY1 + 5, recogBox[4], recogBox[5]])

                last_y = last_y + calcY2 - calcY1 + 15

            newImg = imgEnhance(newImg, sharpness=1.2, contrast=1.2, brightness=1, medianFilter=3, autocontrast=True)
            newImg = newImg.convert('L')
            # Image._show(newImg)

            return newImg, newRecogBoxes
        else:
            return None, newRecogBoxes

if __name__ == '__main__':
    template = ocrTemplate(jsonFile=r'./template.json', docType=1)
    print(template.refBoxes, template.recogBoxes)
