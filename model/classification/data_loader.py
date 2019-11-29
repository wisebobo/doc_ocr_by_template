# -*- coding: utf-8 -*-
import numpy as np
import cv2
import os, glob, itertools
from random import shuffle
from keras.preprocessing.image import img_to_array
from keras.utils import to_categorical

class DataLoader:

	def __init__(self, images_dir, num_classes, batch_size=64, image_shape=(110, 175)):
		self.images_dir = images_dir.replace('\\', '/')
		self.image_shape = image_shape
		(self._w, self._h) = image_shape
		self.num_classes = num_classes
		self.batch_size = batch_size

	def __get_file_list(self, path):

		img_list = glob.glob(path + '/*.[jp][pn]g')

		return img_list

	def load_data(self):

		def get_label(image_file):

			[dirname, filename] = os.path.split(image_file)

			dirname = dirname.replace('\\', '/')

			return dirname.split('/')[-1]


		def load_single_image(image_file):

			img = cv2.imread(image_file, 0)
			img = cv2.resize(img, (self._w, self._h))
			img = img_to_array(img)

			return img


		categories = list(map(self.__get_file_list, list(map(lambda x: os.path.join(self.images_dir, x), os.listdir(self.images_dir)))))
		data_list = list(itertools.chain.from_iterable(categories))

		shuffle(data_list)

		images_data, labels = [], []


		for file in data_list:
			img = load_single_image(file)
			label = get_label(file)

			images_data.append(img)
			labels.append(label)


		images_data = np.array(images_data, dtype='float') / 255.0
		labels = to_categorical(np.array(labels), num_classes=self.num_classes)

		return images_data, labels


if __name__ == '__main__':

	np.set_printoptions(threshold=10, edgeitems=100, suppress=True)

	path = r'E:\Python\MyProgram\AI\img_classification\Samples\image_class-master\dataset\test'

	train_data_loader = DataLoader(images_dir=path, num_classes=8)

	images_data, labels = train_data_loader.load_data()

	print(labels)
