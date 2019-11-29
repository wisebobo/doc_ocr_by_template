# -*- coding: utf-8 -*-
import keras, json, re, cv2, os
import numpy as np
from PIL import Image
from keras.models import Model, Sequential, load_model
from keras.regularizers import l2
from keras import backend as K
from keras.layers import Input, merge, ZeroPadding2D, Flatten, BatchNormalization, Permute, TimeDistributed, Flatten, Lambda
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.convolutional import Conv2D
from keras.layers.pooling import AveragePooling2D, GlobalAveragePooling2D, MaxPooling2D
from keras.layers.normalization import BatchNormalization
from keras.layers.merge import concatenate
from keras.optimizers import Adam
from keras.applications import VGG16, VGG19, ResNet50, InceptionV3, Xception, MobileNet
from keras.preprocessing.image import img_to_array
from keras.callbacks import TensorBoard, ReduceLROnPlateau, EarlyStopping, ModelCheckpoint

from model.classification.data_loader import DataLoader

import tensorflow as tf
import logging
from util.log import logging_elapsed_time

graph = tf.compat.v1.get_default_graph()
# sess = tf.Session(graph=graph)

K.set_image_dim_ordering('tf')


class MODEL(object):

	def __init__(self, input_shape, num_classes):
		self.input_shape = input_shape
		self.num_classes = num_classes

	def mnist_net(self):
		model = Sequential()
		model.add(Conv2D(96, (3,3), input_shape=self.input_shape, padding='same', activation='relu', kernel_initializer='uniform'))
		model.add(Conv2D(128, (3,3), padding='same', activation='relu'))
		model.add(Conv2D(128, (1,1), padding='same', activation='relu'))
		model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
		model.add(Conv2D(256, (3,3), padding='same',activation='relu'))
		model.add(Conv2D(256, (1,1), padding='same',activation='relu'))
		model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
		model.add(Conv2D(512, (3, 3), padding='same', activation='relu'))
		model.add(Conv2D(512, (3, 3), padding='same', activation='relu'))
		model.add(Conv2D(256, (1, 1), padding='same', activation='relu'))
		model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
		model.add(Conv2D(512, (3, 3), padding='same', activation='relu'))
		model.add(Conv2D(512, (3, 3), padding='same', activation='relu'))
		model.add(Conv2D(256, (1, 1), padding='same', activation='relu'))
		model.add(Flatten())
		model.add(Dense(4096,activation='relu'))
		model.add(Dropout(0.5))
		model.add(Dense(2048, activation='relu'))
		model.add(Dropout(0.5))
		model.add(Dense(self.num_classes,activation='softmax'))

		return model

	#VGG16
	def VGG16_TSL(self):
		model = Sequential()
		model.add(Conv2D(64, kernel_size=(3,3), input_shape=self.input_shape, padding='same', activation='relu'))
		model.add(Conv2D(64, kernel_size=(3,3), padding='same', activation='relu'))
		model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
		model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
		model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
		model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
		model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
		model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
		model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
		model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
		model.add(Conv2D(512, (3, 3), padding='same', activation='relu'))
		model.add(Conv2D(512, (3, 3), padding='same', activation='relu'))
		model.add(Conv2D(512, (3, 3), padding='same', activation='relu'))
		model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
		model.add(Conv2D(512, (3, 3), padding='same', activation='relu'))
		model.add(Conv2D(512, (3, 3), padding='same', activation='relu'))
		model.add(Conv2D(512, (3, 3), padding='same', activation='relu'))
		model.add(Flatten())
		model.add(Dense(4096,activation='relu'))
		model.add(Dropout(0.5))
		model.add(Dense(1024,activation='relu'))
		model.add(Dropout(0.5))
		model.add(Dense(self.num_classes,activation='softmax'))

		return model

	# AlexNet
	def AlexNet(self):
		model = Sequential()
		model.add(Conv2D(96, (11, 11), strides=(4, 4), input_shape=self.input_shape, padding='valid',activation='relu', kernel_initializer='uniform'))
		model.add(MaxPooling2D(pool_size=(3, 3), strides=(2, 2)))#26*26
		model.add(Conv2D(256, (5, 5), strides=(1, 1), padding='same', activation='relu', kernel_initializer='uniform'))
		model.add(MaxPooling2D(pool_size=(3, 3), strides=(2, 2)))
		model.add(Conv2D(384, (3, 3), strides=(1, 1), padding='same', activation='relu', kernel_initializer='uniform'))
		model.add(Conv2D(384, (3, 3), strides=(1, 1), padding='same', activation='relu', kernel_initializer='uniform'))
		model.add(Conv2D(256, (3, 3), strides=(1, 1), padding='same', activation='relu', kernel_initializer='uniform'))
		model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
		model.add(Flatten())
		model.add(Dense(4096, activation='relu'))
		model.add(Dropout(0.5))
		model.add(Dense(4096, activation='relu'))
		model.add(Dropout(0.5))
		model.add(Dense(self.num_classes, activation='softmax'))

		return model

	#LeNet
	def LeNet(self):
		model = Sequential()
		model.add(Conv2D(20, (5, 5), padding="same", input_shape=self.input_shape))
		model.add(Activation("relu"))
		model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
		# second set of CONV => RELU => POOL layers
		model.add(Conv2D(50, (5, 5), padding="same"))
		model.add(Activation("relu"))
		model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
		# first (and only) set of FC => RELU layers
		model.add(Flatten())
		model.add(Dense(500))
		model.add(Activation("relu"))

		# softmax classifier
		model.add(Dense(self.num_classes))
		model.add(Activation("softmax"))

		return model

	#ZF_Net,8 layers
	def ZF_Net(self):
		model = Sequential()
		model.add(Conv2D(96, (7, 7), strides=(2, 2), input_shape=self.input_shape, padding='valid', activation='relu', kernel_initializer='uniform'))
		model.add(MaxPooling2D(pool_size=(3, 3), strides=(2, 2)))
		model.add(Conv2D(256, (5, 5), strides=(2, 2), padding='same', activation='relu', kernel_initializer='uniform'))
		model.add(MaxPooling2D(pool_size=(3, 3), strides=(2, 2)))
		model.add(Conv2D(384, (3, 3), strides=(1, 1), padding='same', activation='relu', kernel_initializer='uniform'))
		model.add(Conv2D(384, (3, 3), strides=(1, 1), padding='same', activation='relu', kernel_initializer='uniform'))
		model.add(Conv2D(256, (3, 3), strides=(1, 1), padding='same', activation='relu', kernel_initializer='uniform'))
		model.add(MaxPooling2D(pool_size=(3, 3), strides=(2, 2)))
		model.add(Flatten())
		model.add(Dense(4096, activation='relu'))
		model.add(Dropout(0.5))
		model.add(Dense(4096, activation='relu'))
		model.add(Dropout(0.5))
		model.add(Dense(self.num_classes, activation='softmax'))

		return model

#RESNET
class Resnet_Model(object):

	def __init__(self, input_shape, num_outputs):
		self.input_shape = input_shape
		self.num_outputs = num_outputs

	# @staticmethod
	def build(self, block_fn, repetitions):
		"""Builds a custom ResNet like architecture.
		Args:
			input_shape: The input shape in the form (nb_channels, nb_rows, nb_cols)
			num_outputs: The number of outputs at final softmax layer
			block_fn: The block function to use. This is either `basic_block` or `bottleneck`.
				The original paper used basic_block for layers < 50
			repetitions: Number of repetitions of various block units.
				At each block unit, the number of filters are doubled and the input size is halved
		Returns:
			The keras `Model`.
		"""

		self._handle_dim_ordering()
		block_fn = self._get_block(block_fn)

		input = Input(shape=self.input_shape)
		conv1 = self._conv_bn_relu(filters=64, kernel_size=(7, 7), strides=(2, 2))(input)
		pool1 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2), padding="same")(conv1)

		block = pool1
		filters = 64
		for i, r in enumerate(repetitions):
			block = self._residual_block(block_fn, filters=filters, repetitions=r, is_first_layer=(i == 0))(block)
			filters *= 2

		# Last activation
		block = self._bn_relu(block)

		# Classifier block
		block_shape = K.int_shape(block)
		pool2 = AveragePooling2D(pool_size=(block_shape[ROW_AXIS], block_shape[COL_AXIS]),
								 strides=(1, 1))(block)

		flatten1 = Flatten()(pool2)
		dense = Dense(units=self.num_outputs,
					  activation="softmax")(flatten1)

		model = Model(inputs=input, outputs=dense)
		# model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

		return model

	# @staticmethod
	def build_resnet18(self):
		return self.build(self.basic_block, [2, 2, 2, 2])

	# @staticmethod
	def build_resnet34(self,params):
		return self.build(self.basic_block, [3, 4, 6, 3])

	# @staticmethod
	def build_resnet50(self):
		return self.build(self.bottleneck, [3, 4, 6, 3])

	# @staticmethod
	def build_resnet101(self):
		return self.build(self.bottleneck, [3, 4, 23, 3])

	# @staticmethod
	def build_resnet152(self):
		return self.build(self.bottleneck, [3, 8, 36, 3])

	def _bn_relu(self,input):
		"""Helper to build a BN -> relu block
		"""
		norm = BatchNormalization(axis=CHANNEL_AXIS)(input)
		return Activation("relu")(norm)

	def _conv_bn_relu(self, **conv_params):
		"""Helper to build a conv -> BN -> relu block
		"""
		filters = conv_params["filters"]
		kernel_size = conv_params["kernel_size"]
		strides = conv_params.setdefault("strides", (1, 1))
		kernel_initializer = conv_params.setdefault("kernel_initializer", "he_normal")
		padding = conv_params.setdefault("padding", "same")
		kernel_regularizer = conv_params.setdefault("kernel_regularizer", l2(1.e-4))

		def f(input):
			conv = Conv2D(filters=filters, kernel_size=kernel_size,
						  strides=strides, padding=padding,
						  kernel_initializer=kernel_initializer,
						  kernel_regularizer=kernel_regularizer)(input)
			return self._bn_relu(conv)

		return f


	def _bn_relu_conv(self,**conv_params):
		"""Helper to build a BN -> relu -> conv block.
		This is an improved scheme proposed in http://arxiv.org/pdf/1603.05027v2.pdf
		"""
		filters = conv_params["filters"]
		kernel_size = conv_params["kernel_size"]
		strides = conv_params.setdefault("strides", (1, 1))
		kernel_initializer = conv_params.setdefault("kernel_initializer", "he_normal")
		padding = conv_params.setdefault("padding", "same")
		kernel_regularizer = conv_params.setdefault("kernel_regularizer", l2(1.e-4))

		def f(input):
			activation = self._bn_relu(input)
			return Conv2D(filters=filters, kernel_size=kernel_size,
						  strides=strides, padding=padding,
						  kernel_initializer=kernel_initializer,
						  kernel_regularizer=kernel_regularizer)(activation)

		return f


	def _shortcut(self,input, residual):
		"""Adds a shortcut between input and residual block and merges them with "sum"
		"""
		# Expand channles of shortcut to match residual.
		# Stride appropriately to match residual (width, height)
		# Should be int if network architecture is correctly configured.
		input_shape = K.int_shape(input)
		residual_shape = K.int_shape(residual)
		stride_width = int(round(input_shape[ROW_AXIS] / residual_shape[ROW_AXIS]))
		stride_height = int(round(input_shape[COL_AXIS] / residual_shape[COL_AXIS]))
		equal_channels = input_shape[CHANNEL_AXIS] == residual_shape[CHANNEL_AXIS]

		shortcut = input
		# 1 X 1 conv if shape is different. Else identity.
		if stride_width > 1 or stride_height > 1 or not equal_channels:
			shortcut = Conv2D(filters=residual_shape[CHANNEL_AXIS],
							  kernel_size=(1, 1),
							  strides=(stride_width, stride_height),
							  padding="valid",
							  kernel_initializer="he_normal",
							  kernel_regularizer=l2(0.0001))(input)

		return add([shortcut, residual])


	def _residual_block(self,block_function, filters, repetitions, is_first_layer=False):
		"""Builds a residual block with repeating bottleneck blocks.
		"""
		def f(input):
			for i in range(repetitions):
				init_strides = (1, 1)
				if i == 0 and not is_first_layer:
					init_strides = (2, 2)
				input = block_function(filters=filters, init_strides=init_strides,
									   is_first_block_of_first_layer=(is_first_layer and i == 0))(input)
			return input

		return f


	def basic_block(self,filters, init_strides=(1, 1), is_first_block_of_first_layer=False):
		"""Basic 3 X 3 convolution blocks for use on resnets with layers <= 34.
		Follows improved proposed scheme in http://arxiv.org/pdf/1603.05027v2.pdf
		"""
		def f(input):

			if is_first_block_of_first_layer:
				# don't repeat bn->relu since we just did bn->relu->maxpool
				conv1 = Conv2D(filters=filters, kernel_size=(3, 3),
							   strides=init_strides,
							   padding="same",
							   kernel_initializer="he_normal",
							   kernel_regularizer=l2(1e-4))(input)
			else:
				conv1 = self._bn_relu_conv(filters=filters, kernel_size=(3, 3),
									  strides=init_strides)(input)

			residual = self._bn_relu_conv(filters=filters, kernel_size=(3, 3))(conv1)
			return self._shortcut(input, residual)

		return f


	def bottleneck(self,filters, init_strides=(1, 1), is_first_block_of_first_layer=False):
		"""Bottleneck architecture for > 34 layer resnet.
		Follows improved proposed scheme in http://arxiv.org/pdf/1603.05027v2.pdf
		Returns:
			A final conv layer of filters * 4
		"""
		def f(input):

			if is_first_block_of_first_layer:
				# don't repeat bn->relu since we just did bn->relu->maxpool
				conv_1_1 = Conv2D(filters=filters, kernel_size=(1, 1),
								  strides=init_strides,
								  padding="same",
								  kernel_initializer="he_normal",
								  kernel_regularizer=l2(1e-4))(input)
			else:
				conv_1_1 = self._bn_relu_conv(filters=filters, kernel_size=(1, 1),
										 strides=init_strides)(input)

			conv_3_3 = self._bn_relu_conv(filters=filters, kernel_size=(3, 3))(conv_1_1)
			residual = self._bn_relu_conv(filters=filters * 4, kernel_size=(1, 1))(conv_3_3)
			return self._shortcut(input, residual)

		return f

	def _handle_dim_ordering(self):
		global ROW_AXIS
		global COL_AXIS
		global CHANNEL_AXIS
		if K.image_dim_ordering() == 'tf':
			ROW_AXIS = 1
			COL_AXIS = 2
			CHANNEL_AXIS = 3
		else:
			CHANNEL_AXIS = 1
			ROW_AXIS = 2
			COL_AXIS = 3

	def _get_block(self,identifier):
		if isinstance(identifier, six.string_types):
			res = globals().get(identifier)
			if not res:
				raise ValueError('Invalid {}'.format(identifier))
			return res
		return identifier


class DenseNet_Model(object):

	def __init__(self,
				 image_shape,
				 num_classes,
				 dropout_rate=0.2,
				 weight_decay=1e-4,
				 filters=64):
		self.image_shape = image_shape
		self.dropout_rate = dropout_rate
		self.weight_decay = weight_decay
		self.filters = filters
		self.num_classes = num_classes

	def _dense_block(self, x, nb_layers, nb_filter, growth_rate, dropout_rate=0.2, weight_decay=1e-4):
		for i in range(nb_layers):
			cb = self._conv_block(x, growth_rate, dropout_rate, weight_decay)
			x = concatenate([x, cb])
			nb_filter += growth_rate
		return x, nb_filter


	def _conv_block(self, input, growth_rate, dropout_rate=None, weight_decay=1e-4):
		x = BatchNormalization(epsilon=1.1e-5)(input)
		x = Activation('relu')(x)
		x = Conv2D(growth_rate, (3, 3), kernel_initializer='he_normal', padding='same')(x)
		if dropout_rate:
			x = Dropout(dropout_rate)(x)
		return x


	def _transition_block(self, input, nb_filter, dropout_rate=None, pooltype=1, weight_decay=1e-4):
		x = BatchNormalization(epsilon=1.1e-5)(input)
		x = Activation('relu')(x)
		x = Conv2D(nb_filter, (1, 1), kernel_initializer='he_normal', padding='same', use_bias=False,
				   kernel_regularizer=l2(weight_decay))(x)

		if dropout_rate:
			x = Dropout(dropout_rate)(x)

		if pooltype == 2:
			x = AveragePooling2D((2, 2), strides=(2, 2))(x)
		elif pooltype == 1:
			x = ZeroPadding2D(padding=(0, 1))(x)
			x = AveragePooling2D((2, 2), strides=(2, 1))(x)
		elif pooltype == 3:
			x = AveragePooling2D((2, 2), strides=(2, 1))(x)

		return x, nb_filter

	def build_model(self):
		input = Input(shape=self.image_shape, name="the_input")
		nb_filter = self.filters

		x = Conv2D(nb_filter, (5, 5), strides=(2, 2), kernel_initializer='he_normal', padding='same',
				   use_bias=False, kernel_regularizer=l2(self.weight_decay))(input)

		# 64 +  8 * 8 = 128
		x, nb_filter = self._dense_block(x, 8, nb_filter, 8, None, self.weight_decay)
		# 128
		x, nb_filter = self._transition_block(x, 128, self.dropout_rate, 2, self.weight_decay)

		# 128 + 8 * 8 = 192
		x, nb_filter = self._dense_block(x, 8, nb_filter, 8, None, self.weight_decay)
		# 192->128
		x, nb_filter = self._transition_block(x, 128, self.dropout_rate, 2, self.weight_decay)

		# 128 + 8 * 8 = 192
		x, nb_filter = self._dense_block(x, 8, nb_filter, 8, None, self.weight_decay)

		x = BatchNormalization(axis=-1, epsilon=1.1e-5)(x)
		x = Activation('relu')(x)

		x = Permute((2, 1, 3), name='permute')(x)
		x = TimeDistributed(Flatten(), name='flatten')(x)
		y_pred = Dense(self.num_classes, name='out', activation='softmax')(x)

		model = Model(inputs=input, outputs=y_pred)

		return model



class img_class_model(object):

	@logging_elapsed_time('Load image classification model')
	def __init__(self, config_file, weight_file=None, model_file=None):

		config = self.load_config(config_file)

		self.model_name = config['model_name']
		self.checkpoints_path = './checkpoints/' + self.model_name
		self.save_weigths_file_path = "./checkpoints/weights-%s-{epoch:02d}.hdf5" % self.model_name
		self.monitor = config['monitor']
		self.lr_reduce_patience = config['lr_reduce_patience']
		self.early_stop_patience = config['early_stop_patience']
		self.batch_size = config['batch_size']
		self.epochs = config['epochs']
		self.initial_epoch = config['initial_epoch']
		self.image_shape = (config['image_height'], config['image_width'], 1)
		self.classes = config['num_classes']
		self.lr = config['lr']

		self.label_names = {
			"0": "Passport",
			"1": "CHN ID Card",
			"2": "HK ID Card",
			"3": "HK ID Card (Old)",
			"4": "Macau ID Card",
			"5": "Macau ID Card (Old)",
			"6": "Macau ID Card MRZ",
			"7": "CN to HK/Macau Entry Card",
			"8": "CN to HK/Macau Entry Book (Old)",
			"9": "CN to TW Entry Card",
			"10": "HK/Macau to CN Entry Card",
			"11": "HK/Macau to CN Entry Card (Old)",
			"12": "TW to CN Entry Card",
			"13": "TW to CN Entry Book (Old)",
			"14": "AU Driver License - NSW - New South Wales",
			"15": "AU Driver License - VIC - Victoria",
			"16": "AU Driver License - ACT - Australian Capital Territory",
			"17": "AU Driver License - QLD - Queensland",
			"18": "AU Driver License - WA - Western",
			"19": "AU Driver License - NT - Northern Territory",
			"20": "AU Driver License - TAS - Tasmania",
			"21": "AU Driver License - SA - South",
			"22": "NZ Driver License"
		}

		if model_file is not None:
			self.model = load_model(model_file)
		else:
			self.model = self.build()

			if weight_file is not None:
				self.model.load_weights(weight_file)

	def build(self):

		if self.model_name == 'VGG16':
			model = VGG16(include_top=True, weights=None, input_tensor=None, input_shape=self.image_shape, pooling='max', classes=self.classes)
		elif self.model_name == 'VGG19':
			model = VGG19(include_top=True, weights=None, input_tensor=None, input_shape=self.image_shape, pooling='max', classes=self.classes)
		elif self.model_name == 'ResNet50':
			model = ResNet50(include_top=True, weights=None, input_tensor=None, input_shape=self.image_shape, pooling='max', classes=self.classes)
		elif self.model_name == 'InceptionV3':
			model = InceptionV3(include_top=True, weights=None, input_tensor=None, input_shape=self.image_shape, pooling='max', classes=self.classes)
		elif self.model_name == 'Xception':
			model = Xception(include_top=True, weights=None, input_tensor=None, input_shape=self.image_shape, pooling='max', classes=self.classes)
		elif self.model_name == 'MobileNet':
			model = MobileNet(include_top=True, weights=None, input_tensor=None, input_shape=self.image_shape, pooling='max', classes=self.classes)
		elif self.model_name == 'DenseNet':
			model = DenseNet_Model(self.image_shape, self.classes).build_model()
		elif self.model_name == 'ResNet18':
			model = Resnet_Model(self.image_shape, self.classes).build_resnet18()
		elif self.model_name == 'ResNet34':
			model = Resnet_Model(self.image_shape, self.classes).build_resnet34()
		elif self.model_name == 'ResNet101':
			model = Resnet_Model(self.image_shape, self.classes).build_resnet101()
		elif self.model_name == 'ResNet152':
			model = Resnet_Model(self.image_shape, self.classes).build_resnet152()
		elif self.model_name == 'AlexNet':
			model = MODEL(self.image_shape, self.classes).AlexNet()
		elif self.model_name == 'LeNet':
			model = MODEL(self.image_shape, self.classes).LeNet()
		elif self.model_name == 'ZF_Net':
			model = MODEL(self.image_shape, self.classes).ZF_Net()
		elif self.model_name =='mnist_net':
			model = MODEL(self.image_shape, self.classes).mnist_net()
		elif self.model_name == 'VGG16_TSL':
			model = MODEL(self.image_shape, self.classes).VGG16_TSL()

		adam = Adam(lr=self.lr, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0)
		model.compile(loss="categorical_crossentropy", optimizer=adam, metrics=["accuracy"])

		return model

	def train(self, train_data_loader: DataLoader, valid_data_loader: DataLoader):

		X_train, y_train = train_data_loader.load_data()
		X_test, y_test = valid_data_loader.load_data()

		tensorboard = TensorBoard(log_dir=self.__mkdir(self.checkpoints_path), histogram_freq=0, batch_size=self.batch_size, write_graph=True, write_grads=False)

		lr_reduce = ReduceLROnPlateau(monitor=self.monitor, factor=0.1, patience=self.lr_reduce_patience, verbose=1, mode='auto',  cooldown=0)

		early_stop = EarlyStopping(monitor=self.monitor, min_delta=0, patience=self.early_stop_patience, verbose=1, mode='auto')

		checkpoint = ModelCheckpoint(self.save_weigths_file_path, monitor=self.monitor, verbose=1, save_best_only=True, save_weights_only=True, mode='auto', period=1)

		self.model.fit(X_train, y_train,
			validation_data=(X_test, y_test),
			epochs=self.epochs,
			batch_size=self.batch_size,
			initial_epoch=self.initial_epoch,
			callbacks=[early_stop, checkpoint, lr_reduce, tensorboard],
			verbose=1)

	def __mkdir(self, path):
		if not os.path.exists(path):
			return os.mkdir(path)
		return path

	def __load_single_image(self, image):

		if type(image) == str:
			img = Image.open(image)
		else:
			img = image

		img = img.convert('L')
		img = img.resize((self.image_shape[1], self.image_shape[0]), Image.ANTIALIAS)
		img = np.array([img_to_array(img)], dtype='float') / 255.0

		return img

	@logging_elapsed_time('Image classification - Predict')
	def predict(self, img_file):

		img = self.__load_single_image(img_file)

		# with sess.as_default():
		with graph.as_default():
			confidences = self.model.predict(img).tolist()[0]

		for i, pred in enumerate(confidences):
			logging.info('%2d - %-70s\t\t\t%f' % (i, self.label_names[str(i)], pred))

		return confidences.index(max(confidences)), max(confidences)

	@staticmethod
	def save_config(obj, config_path: str):
		with open(config_path, 'w+') as outfile:
			json.dump(obj.config(), outfile)

	@staticmethod
	def load_config(config_path: str):
		with open(config_path, 'r') as infile:

			json_raw = ''.join(infile.readlines())
			json_raw = re.sub(re.compile('(//[\\s\\S]*?\n)'), '', json_raw)
			json_raw = re.sub(re.compile('(/\*[\\s\\S]*?/)'), '', json_raw)

			return dict(json.loads(json_raw))



if __name__ == '__main__':

	model_obj = img_class_model(image_shape=(110,175,1), classes=8, model_name="ResNet50", lr=0.0005)
	model = model_obj.build()
