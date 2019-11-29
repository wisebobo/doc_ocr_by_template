# -*- coding:utf-8 -*-
import os, cv2, re, base64, logging
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
from skimage import io
from operator import itemgetter

def isBase64Str(str):
    if re.match('^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)$', str):
        return True
    else:
        return False

def base64_to_bytes(base64Str):
    base64_data = re.sub('^data:image/.+;base64,', '', base64Str)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    return image_data

def bytes_to_base64(byte_data):
    base64_str = base64.b64encode(byte_data).decode()
    return base64_str

def PIL_to_bytes(img):
    output_buffer = BytesIO()
    img.save(output_buffer, format='JPEG')
    byte_data = output_buffer.getvalue()
    return byte_data

def PIL_to_ndarray(image):
    return np.asarray(image)

def ndarray_to_PIL(image):
    return Image.fromarray(image)

def readImage(image, outFormat, outFile=None):
    if type(image).__name__ == 'str':
        if isBase64Str(image):
            img_data = base64_to_bytes(image)
            if outFormat == 'Ndarray':
                img = io.imread(img_data)
            elif outFormat == 'PIL':
                img = Image.open(img_data).convert('RGB')
            elif outFormat == 'Base64':
                img = image
            elif outFormat == 'File':
                img = Image.open(img_data).convert('RGB')
                img.save(outFile, format='JPEG')
            elif outFormat == 'Bytes':
                img = img_data
        elif os.path.exists(image):
            if outFormat == 'Ndarray':
                img = io.imread(image)
            elif outFormat == 'PIL':
                img = Image.open(image).convert('RGB')
            elif outFormat == 'Base64':
                img = Image.open(image).convert('RGB')
                img = bytes_to_base64(PIL_to_bytes(img))
            elif outFormat == 'File':
                img = Image.open(image)
                img.save(outFile, format='JPEG')
            elif outFormat == 'Bytes':
                with open(image, 'rb') as fp:
                    img = fp.read()
    elif type(image).__name__ == 'Image':
        if outFormat == 'Ndarray':
            img = PIL_to_ndarray(image)
        elif outFormat == 'PIL':
            img = image
        elif outFormat == 'Base64':
            img = bytes_to_base64(PIL_to_bytes(image))
        elif outFormat == 'File':
            img = image
            img.save(outFile, format='JPEG')
        elif outFormat == 'Bytes':
            img = PIL_to_bytes(image)
    elif type(image).__name__ == 'ndarray':
        if outFormat == 'Ndarray':
            img = image
        elif outFormat == 'PIL':
            img = ndarray_to_PIL(image)
        elif outFormat == 'Base64':
            img = ndarray_to_PIL(image)
            img = bytes_to_base64(PIL_to_bytes(img))
        elif outFormat == 'File':
            img = ndarray_to_PIL(image)
            img.save(outFile, format='JPEG')
        elif outFormat == 'Bytes':
            img = ndarray_to_PIL(image)
            img = PIL_to_bytes(img)
    else:
        img = image

    return img


def captureFace(image):
    try:
        np_img = readImage(image, outFormat='Ndarray')

        faces_cascade = cv2.CascadeClassifier('model/haarcascade_frontalface_default.xml')

        face_locations = faces_cascade.detectMultiScale(np_img, 1.3, 5)

        if len(face_locations) > 0:
            face_locations = sorted(face_locations, key=itemgetter(2,), reverse=True)
            (x, y, width, height) = face_locations[0]
            logging.warn(face_locations)
            top = int(y - 50)
            right = int(x + width * 1.1)
            bottom = int(y + height * 1.1)
            left = int(x - 20)

            face_img = image.crop((left, top, right, bottom))
            return readImage(face_img, outFormat='Base64')
        else:
            return None
    except Exception as e:
        logging.error(str(e))
        return None


if __name__ == '__main__':
    img1 = r"..\templates\Samples\04 - MACAU_ID_002.jpg"

    outImg3 = readImage(img1, outFormat='PIL')
    outImg4 = readImage(img1, outFormat='Ndarray')
    outImg5 = readImage(img1, outFormat='Base64')
    outImg6 = readImage(img1, outFormat='Bytes')
    outImg7 = readImage(outImg3, outFormat='Base64')

    print(type(outImg3).__name__)
    print(type(outImg7).__name__)
    print(outImg7)
