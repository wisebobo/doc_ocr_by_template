# -*- coding:utf-8 -*-

import os, cv2, re, base64, sys
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage import io
from skimage.feature import canny
from skimage.color import rgb2gray
from skimage.transform import hough_line, hough_line_peaks, rotate
from util.log import logging_elapsed_time

sys.path.append("../")

from util.readImage import readImage

class imageDeskew(object):

    def __init__(self, sigma=3.0, num_peaks=20, r_angle=0):

        self.piby4 = np.pi / 4
        self.sigma = sigma
        self.num_peaks = num_peaks
        self.r_angle = r_angle

    def __get_max_freq_elem(self, arr):

        max_arr = []
        freqs = {}
        for i in arr:
            if i in freqs:
                freqs[i] += 1
            else:
                freqs[i] = 1

        sorted_keys = sorted(freqs, key=freqs.get, reverse=True)
        max_freq = freqs[sorted_keys[0]]

        for k in sorted_keys:
            if freqs[k] == max_freq:
                max_arr.append(k)

        return max_arr

    def __compare_sum(self, value):
        if value >= 44 and value <= 46:
            return True
        else:
            return False

    def __calculate_deviation(self, angle):

        angle_in_degrees = np.abs(angle)
        deviation = np.abs(self.piby4 - angle_in_degrees)

        return deviation

    @logging_elapsed_time('Calculate skew angle')
    def determine_skew(self, img):

        img = readImage(img, outFormat='Ndarray')
        img = rgb2gray(img)

        edges = canny(img, sigma=self.sigma)
        h, a, d = hough_line(edges)
        _, ap, _ = hough_line_peaks(h, a, d, num_peaks=self.num_peaks)

        if len(ap) == 0:
            return {"Image File": img_file, "Message": "Bad Quality"}

        absolute_deviations = [self.__calculate_deviation(k) for k in ap]
        average_deviation = np.mean(np.rad2deg(absolute_deviations))
        ap_deg = [np.rad2deg(x) for x in ap]

        bin_0_45 = []
        bin_45_90 = []
        bin_0_45n = []
        bin_45_90n = []

        for ang in ap_deg:

            deviation_sum = int(90 - ang + average_deviation)
            if self.__compare_sum(deviation_sum):
                bin_45_90.append(ang)
                continue

            deviation_sum = int(ang + average_deviation)
            if self.__compare_sum(deviation_sum):
                bin_0_45.append(ang)
                continue

            deviation_sum = int(-ang + average_deviation)
            if self.__compare_sum(deviation_sum):
                bin_0_45n.append(ang)
                continue

            deviation_sum = int(90 + ang + average_deviation)
            if self.__compare_sum(deviation_sum):
                bin_45_90n.append(ang)

        angles = [bin_0_45, bin_45_90, bin_0_45n, bin_45_90n]
        lmax = 0

        for j in range(len(angles)):
            l = len(angles[j])
            if l > lmax:
                lmax = l
                maxi = j

        if lmax:
            ans_arr = self.__get_max_freq_elem(angles[maxi])
            ans_res = np.mean(ans_arr)

        else:
            ans_arr = self.__get_max_freq_elem(ap_deg)
            ans_res = np.mean(ans_arr)

        data = {
            "Average Deviation from pi/4": average_deviation,
            "Estimated Angle": ans_res,
            "Angle bins": angles}

        # print(data)

        return ans_res

    def __display(self, img):

        plt.imshow(img)
        plt.show()

    @logging_elapsed_time('Deskew image')
    def deskew(self, imgFile, angle):

        # img = self.readImg(imgFile)
        img = readImage(imgFile, outFormat='PIL')

        if angle >= 10 and angle <= 90:
            rot_angle = angle - 90 + self.r_angle
        elif angle >= -45 and angle < -10:
            rot_angle = angle - 90 + self.r_angle
        elif angle >= -90 and angle < -45:
            rot_angle = 90 + angle + self.r_angle
        else:
            rot_angle = 0

        if rot_angle:
            rotated = img.rotate(rot_angle, Image.BICUBIC, expand=True)
        else:
            rotated = img

        # self.__display(rotated)

        return rotated


if __name__ == '__main__':

    imgFile = r'..\templates\Samples\04 - MACAU_ID_002.jpg'

    img = imageDeskew()
    img.deskew(imgFile)
