# -*- coding:utf-8 -*-
import re, sys
import time, logging
from collections import OrderedDict
from util.MRZ import MRZ, MRZOCRCleaner
from util.ctc2hanzi import ctc_code
from util.name2pinyin import ChineseName
from util.CHN_ID_Verify import CHNIdNumber
from util.log import logging_elapsed_time


class doc_etl(object):

    def __init__(self, img, vendor, ocr_rslt, doc_type):
        self._img = img
        self._vendor = vendor
        self._doc_type = doc_type
        self._ocr_rslt = ocr_rslt

        self._doc_number = ''
        self._first_name = ''
        self._last_name = ''
        self._local_name = ''
        self._local_name_GBK = ''
        self._local_name_last = ''
        self._local_name_first = ''
        self._GBKCode_last = ''
        self._GBKCode_first = ''
        self._DOB = ''
        self._sex = ''
        self._nationality = ''
        self._DOE = ''
        self._address = ''
        self._mrz_type = ''
        self._mrz_line1 = ''
        self._mrz_line2 = ''
        self._mrz_line3 = ''
        self._valid_score = 0

        if self._doc_type in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]:
            self._country = 'CHN'
            self._nationality = 'CHN'
        elif self._doc_type in [14, 15, 16, 17, 18, 19, 20, 21]:
            self._country = 'AUS'
            self._nationality = 'AUS'
        elif self._doc_type in [22]:
            self._country = 'NZL'
            self._nationality = 'NZL'
        else:
            self._country = ''
            self._nationality = ''

        if self._doc_type in [1, 7, 8, 9, 10, 11, 12, 13]:
            self._date_format = '%Y%m%d'
        elif self._doc_type in [2, 3, 4, 5, 6, 15, 19, 21, 22]:
            self._date_format = '%d%m%Y'
        elif self._doc_type in [14, 16, 17, 18, 20]:
            self._date_format = '%d%b%Y'
        else:
            self._date_format = '%Y%m%d'

        self.doc_type_dict = {
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
            "15": "AU Driver License - VA - Victoria Australia",
            "16": "AU Driver License - ACT - Australian Capital Territory",
            "17": "AU Driver License - QLD - Queensland",
            "18": "AU Driver License - WA - Western Australia",
            "19": "AU Driver License - NT - Northern Territory",
            "20": "AU Driver License - TAS - Tasmania",
            "21": "AU Driver License - SA - South Australia",
            "22": "NZ Driver License"
        }

        self.mrz_type_dict = {
            "TD3": "Passport",
            "CHNHK2000": "CN to HK/Macau Entry Book (Old)",
            "CHNTW2000": "CH to TW Entry Book (Old)",
            "TWCHN2000": "TW to CN Entry Book (Old)",
            "CHNHK2014": "CN to HK/Macau Entry Card",
            "CHNTW2014": "CN to TW Entry Card"
        }

        logging.info('Received image as : ' + self.doc_type_dict[str(self._doc_type)])

        if self._vendor == 'Face++_Template':
            self._parse_by_template()
        else:
            if self._doc_type in [0, 5, 6]:
                self._parse_data()
            else:
                self._parse_by_template()

        self._calc_score()

    def __repr__(self):
        return "DOC OCR({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})".format(self._vendor, self._valid_score,
                                                                        self._doc_number, self._first_name,
                                                                        self._last_name, self._local_name, self._DOB,
                                                                        self._sex)

    def _calc_score(self):
        try:
            self._valid_score = 0

            if self._doc_number:
                self._valid_score += 25

            if self._DOB:
                self._valid_score += 20

            if self._DOE:
                self._valid_score += 10

            if self._local_name or self._local_name_GBK:
                self._valid_score += 5

            if self._last_name:
                self._valid_score += 15

            if self._first_name:
                self._valid_score += 15

            if self._sex:
                self._valid_score += 10

            if self._address:
                self._valid_score += 5

            if self._nationality:
                self._valid_score += 5
        except Exception as e:
            logging.error('%s: Error when running function "%s", error = %s' % (self._vendor, sys._getframe().f_code.co_name, str(e)))

    def to_dict(self):
        # Converts this object to an (ordered) dictionary of field-value pairs.
        result = OrderedDict()
        result['valid_score'] = 0
        result['vendor'] = self._vendor
        try:
            result['valid_score'] = self._valid_score
            if self._valid_score > 0:
                result['doc_number'] = self._doc_number.strip()
                result['first_name'] = self._first_name.strip()
                result['last_name'] = self._last_name.strip()
                result['local_name'] = self._local_name.strip()
                result['local_name_GBK'] = self._local_name_GBK.strip()
                result['date_of_birth'] = self._DOB
                result['sex'] = self._sex
                result['country'] = self._country.strip()
                result['nationality'] = self._nationality.strip()
                result['date_of_expiry'] = self._DOE
                result['address'] = self._address.strip()
                result['doc_type'] = self._doc_type
                result['mrz_type'] = self._mrz_type
                result['mrz_line1'] = self._mrz_line1.strip()
                result['mrz_line2'] = self._mrz_line2.strip()
                result['mrz_line3'] = self._mrz_line3.strip()
        except Exception as e:
            logging.error('%s: Error when running function "%s", error = %s' % (self._vendor, sys._getframe().f_code.co_name, str(e)))
        finally:
            return result

    def _convCTC2GBK(self, ctcCode):
        try:
            local_name = ''
            tmpValue = re.sub('[^0-9]', '', ctcCode)

            if tmpValue.isdigit():
                name_len = int(len(tmpValue) / 4)
                for i in range(name_len):
                    temp_code = tmpValue[0 + i * 4:4 + i * 4]
                    try:
                        local_name = local_name + ''.join(ctc_code[temp_code])
                    except KeyError as e:
                        logging.error(self._vendor + ': Unable to convert CTC code (' + temp_code + ') to GBK')
        except Exception as e:
            logging.error('%s: Error when running function "%s", error = %s' % (self._vendor, sys._getframe().f_code.co_name, str(e)))
        finally:
            return local_name

    def _parse_data(self):
        try:
            if self._doc_type in [0, 6, 7, 8, 9, 13]:
                mrz_valid = self._getMrz(self._ocr_rslt)

                if mrz_valid:
                    if self._mrz_type in ['CHNHK2014', 'CHNTW2014']:
                        self._recog_chn_hk_tw_2014(self._ocr_rslt)
                    elif self._mrz_type in ['CHNHK2000', 'CHNTW2000', 'TWCHN2000']:
                        self._recog_chn_hk_tw_2000(self._ocr_rslt)

            elif self._doc_type in [5]:
                self._recog_macau_id_old(self._ocr_rslt)
        except Exception as e:
            logging.error('%s: Error when running function "%s", error = %s' % (self._vendor, sys._getframe().f_code.co_name, str(e)))


    def _parse_by_template(self):

        try:
            for key, value in self._ocr_rslt.items():
                tmpValue = value.upper()

                if key == 'DOB':
                    if self._date_format == '%d%b%Y':
                        DOB = re.sub('[^0-9A-Z]', '', tmpValue)
                    else:
                        DOB = re.sub('[^0-9]', '', tmpValue)

                    if self._check_date(DOB, self._date_format):
                        self._DOB = time.strftime('%Y-%m-%d', time.strptime(DOB, self._date_format))

                elif key == 'expiryDate':
                    if self._date_format == '%d%b%Y':
                        DOE = re.sub('[^0-9A-Z]', '', tmpValue)
                    else:
                        DOE = re.sub('[^0-9]', '', tmpValue)

                    if self._doc_type == 17:
                        self._date_format = '%d%m%y'

                    if self._check_date(DOE, self._date_format):
                        self._DOE = time.strftime('%Y-%m-%d', time.strptime(DOE, self._date_format))

                elif key == 'docNumber':
                    doc_num = tmpValue.replace('（', '(').replace('）', ')')
                    self._doc_number = re.sub('[^0-9A-Z()]', '', doc_num)

                elif key == 'Sex':
                    if '女' in tmpValue or 'F' in tmpValue:
                        self._sex = 'F'
                    elif '男' in tmpValue or 'M' in tmpValue:
                        self._sex = 'M'

                elif key == 'localName':
                    self._local_name = tmpValue.replace(' ', '')

                elif key == 'localName_Last':
                    self._local_name_last = tmpValue.replace(' ', '')

                elif key == 'localName_First':
                    self._local_name_first = tmpValue.replace(' ', '')

                elif key == 'GBKCode':
                    self._local_name_GBK = self._convCTC2GBK(tmpValue)

                elif key == 'GBKCode_Last':
                    self._GBKCode_last = re.sub('[^0-9]', '', tmpValue)

                elif key == 'GBKCode_First':
                    self._GBKCode_first = re.sub('[^0-9]', '', tmpValue)

                elif key == 'Name':
                    tmpValue = tmpValue.replace('，', ',')
                    eng_name = re.sub('[^A-Z ,]', '', tmpValue)
                    if ',' in eng_name:
                        name = eng_name.split(',')
                    else:
                        name = eng_name.split(' ')

                    if len(name):
                        if self._doc_type in [14]:
                            self._last_name = re.sub('[^A-Z ]', '', name[-1])
                            self._first_name = re.sub('[^A-Z ]', '', ' '.join(name[:-1]).strip())
                        else:
                            self._last_name = re.sub('[^A-Z ]', '', name[0])
                            self._first_name = re.sub('[^A-Z ]', '', ' '.join(name[1:]).strip())

                elif key == 'lastName':
                    self._last_name = re.sub('[^A-Z ]', '', tmpValue)

                elif key == 'firstName':
                    self._first_name = re.sub('[^A-Z ]', '', tmpValue)

                elif key == 'address':
                    self._address = tmpValue

                elif key == 'mrzLine1':
                    tmpValue = tmpValue.replace('く', '<').replace('≤', '<').upper()
                    self._mrz_line1 = re.sub('[^0-9A-Z<]', '', tmpValue)
                elif key == 'mrzLine2':
                    tmpValue = tmpValue.replace('く', '<').replace('≤', '<').upper()
                    self._mrz_line2 = re.sub('[^0-9A-Z<]', '', tmpValue)
                elif key == 'mrzLine3':
                    tmpValue = tmpValue.replace('く', '<').replace('≤', '<').upper()
                    self._mrz_line3 = re.sub('[^0-9A-Z<]', '', tmpValue)

            # Some other further extraction / validation
            if self._doc_type == 1:
                if self._local_name:
                    self._last_name, self._first_name = ChineseName(self._local_name)

                if self._doc_number:
                    # Extract Document ID
                    doc_num_list = []
                    doc_num_list.append(self._doc_number)
                    doc_number_1 = MRZOCRCleaner.apply(doc_num_list, formatType='CHNID')
                    doc_number_1 = ''.join(doc_number_1)
                    doc_number_1 = ''.join(re.findall(r"[0-9X]+", doc_number_1))
                    doc_number_2 = ''.join(re.findall(r"[0-9X]+", self._doc_number))

                    logging.info('doc_number_0 = ' + self._doc_number)
                    logging.info('doc_number_1 = ' + doc_number_1)
                    logging.info('doc_number_2 = ' + doc_number_2)

                    doc_number = None
                    if CHNIdNumber.verify_id(self._doc_number):
                        doc_number = self._doc_number
                    elif CHNIdNumber.verify_id(doc_number_1):
                        doc_number = doc_number_1
                    elif CHNIdNumber.verify_id(doc_number_2):
                        doc_number = doc_number_2
                    else:
                        logging.info('Invalid CHN ID')

                    if doc_number is not None:
                        self._doc_number = doc_number
                        self._DOB = CHNIdNumber(doc_number).get_birthday()
                        sex = CHNIdNumber(doc_number).get_sex()
                        if sex == 0:
                            self._sex = 'F'
                        elif sex == 1:
                            self._sex = 'M'

            elif self._doc_type in [2, 3]:

                if self._doc_number:
                    if self._validate_hk_id(self._doc_number):
                        pass
                    else:
                        self._doc_number = ''

            elif self._doc_type == 4:

                if self._local_name_last and self._local_name_first:
                    self._local_name = self._local_name_last + self._local_name_first

                if self._GBKCode_last and self._GBKCode_first:
                    GBKCode = self._GBKCode_last + self._GBKCode_first
                    self._local_name_GBK = self._convCTC2GBK(GBKCode)

                if self._doc_number:
                    self._doc_number = self._get_macau_id(self._doc_number)

            elif self._doc_type == 6:
                mrzString = []
                mrzString.append(self._mrz_line1)
                mrzString.append(self._mrz_line2)
                mrzString.append(self._mrz_line3)

                mrz_valid = self._getMrz(mrzString)

            elif self._doc_type in [7, 9]:
                mrzString = []
                mrzString.append(self._mrz_line1)

                mrz_valid = self._getMrz(mrzString)

            elif self._doc_type in [8, 13]:
                mrzString = []
                mrzString.append(self._mrz_line1)
                mrzString.append(self._mrz_line2)

                mrz_valid = self._getMrz(mrzString)
        except Exception as e:
            logging.error('%s: Error when running function "%s", error = %s' % (self._vendor, sys._getframe().f_code.co_name, str(e)))


    def _check_date(self, date, format='%d-%m-%Y'):
        try:
            __date = time.strptime(date, format)

            # Date difference should be less than 100 years
            __earliestYear = str(int(time.strftime("%Y")) - 100)
            __earliestDate = time.strptime(__earliestYear + "0101", "%Y%m%d")

            __futureYear = str(int(time.strftime("%Y")) + 20)
            __futureDate = time.strptime(__futureYear + "0101", "%Y%m%d")

            if __date >= __earliestDate and __date <= __futureDate:
                return True
            else:
                return False
        except ValueError:
            return False


    def _getMrz(self, ocr_string):
        try:
            mrz_list = []
            if len(ocr_string) >= 5:
                tempString = ocr_string[-5:]
            else:
                tempString = ocr_string

            for item in tempString:
                item = item.replace(' ', '').replace('く', '<').replace('≤', '<').upper()

                if len(item) > 44:
                    item = item[0:44]

                if len(item) >= 28 and re.match('^[0-9A-Z<]+$', item):
                    mrz_list.append(item)

            if self._doc_type == 7:
                mrz_type = 'CHNHK2014'
            elif self._doc_type == 8:
                mrz_type = 'CHNHK2000'
            elif self._doc_type == 9:
                mrz_type = 'CHNTW2014'
            elif self._doc_type == 13:
                mrz_type = 'TWCHN2000'
            else:
                mrz_type = None

            mrz_list = MRZOCRCleaner.apply(mrz_list, mrz_type)
            mrz = MRZ(mrz_list, mrz_type)

            logging.info(self._vendor + ": score = " + str(mrz.valid_score) + "; mrz_list = " + str(mrz_list))

            if mrz.valid_score > 50:
                self._doc_number = mrz.number.replace('<', '')

                name = mrz.names.replace('<', '')
                self._first_name = name
                self._last_name = mrz.surname.replace('<', '')
                if self._contain_zh(name):
                    self._local_name = name
                    self._last_name, self._first_name = ChineseName(self._local_name)

                if len(mrz.date_of_birth) == 6:
                    if time.strptime(mrz.date_of_birth, '%y%m%d') > time.localtime(time.time()):
                        self._DOB = time.strftime('%Y-%m-%d', time.strptime('19' + mrz.date_of_birth, '%Y%m%d'))
                    else:
                        self._DOB = time.strftime('%Y-%m-%d', time.strptime(mrz.date_of_birth, '%y%m%d'))
                elif len(mrz.date_of_birth) == 8:
                    self._DOB = time.strftime('%Y-%m-%d', time.strptime(mrz.date_of_birth, '%Y%m%d'))
                else:
                    self._DOB = mrz.date_of_birth

                if mrz.sex:
                    self._sex = mrz.sex

                self._country = mrz.country
                self._nationality = mrz.nationality.replace('<', '')

                if len(mrz.expiration_date) == 6:
                    self._DOE = time.strftime('%Y-%m-%d', time.strptime(mrz.expiration_date, '%y%m%d'))
                elif len(mrz.expiration_date) == 8:
                    self._DOE = time.strftime('%Y-%m-%d', time.strptime(mrz.expiration_date, '%Y%m%d'))
                else:
                    self._DOE = mrz.expiration_date

                self._mrz_type = mrz.mrz_type
                self._mrz_line1 = mrz.mrz_line1
                self._mrz_line2 = mrz.mrz_line2
                self._mrz_line3 = mrz.mrz_line3
                self._valid_score = mrz.valid_score

                if mrz.mrz_type == 'TD1' and mrz.country == 'MAC':
                    self._doc_number = '%s(%s)' % (self._doc_number[0:7], self._doc_number[-1])

                return True
            else:
                return False
        except Exception as e:
            logging.error('%s: Error when running function "%s", error = %s' % (self._vendor, sys._getframe().f_code.co_name, str(e)))
            return False


    '''
    ======================================
    港澳通行证2014版，卡式
    台湾通行证2014版，卡式
    ======================================
    '''
    def _recog_chn_hk_tw_2014(self, ocr_string):

        try:
            logging.info('Trying to recognize as CHN TO HK/MACAU/TW ENTRY CARD ...')

            eng_name = ''
            zh_name_found = False

            for i in range(1, 4):
                tempName = ocr_string[i]

                temp_str_1 = ''.join(re.findall(r"[0-9a-zA-Z]+", tempName))
                doc_num_list = []
                doc_num_list.append(temp_str_1)
                doc_number_1 = MRZOCRCleaner.apply(doc_num_list, formatType='CHNHK2014ID')
                doc_number_1 = ''.join(doc_number_1)

                if self._doc_number in tempName or self._doc_number in doc_number_1:
                    pass
                elif self._contain_zh(tempName) and not zh_name_found:
                    tempName = tempName.replace(' ', '')
                    tempName = re.findall(r'[\u4e00-\u9fa5]', tempName)
                    tempName = ''.join(tempName)

                    self._local_name = tempName

                    zh_name_found = True
                elif self._validate_eng_name(tempName):
                    eng_name = eng_name + tempName

                    if len(eng_name):
                        eng_name = eng_name.replace(',', ' ').replace('.', ' ').replace('/', ' ')

                        name = eng_name.split(' ')

                        if len(name):
                            self._last_name = re.sub('[^a-zA-Z ]', '', name[0].strip())
                            self._first_name = re.sub('[^a-zA-Z ]', '', ' '.join(name[1:]).strip())

            if zh_name_found:
                self._last_name, self._first_name = ChineseName(self._local_name)

            if len(self._last_name.strip()) and len(self._first_name.strip()):
                self._valid_score += 10

            if len(ocr_string) >= 3:
                for temp_sex in ocr_string[3:]:
                    if '女' in temp_sex:
                        self._sex = 'F'
                        break
                    elif '男' in temp_sex:
                        self._sex = 'M'
                        break
        except Exception as e:
            logging.error('%s: Error when running function "%s", error = %s' % (self._vendor, sys._getframe().f_code.co_name, str(e)))
        finally:
            logging.info(self.to_dict())

    '''
    ======================================
    港澳通行证2000版，本式
    大陆居民往来台湾通行证 v2000
    台湾居民往来大陆通行证 v2000
    ======================================
    '''
    def _recog_chn_hk_tw_2000(self, ocr_string):

        try:
            eng_name = ''

            for i in range(1, 5):
                tempName = ocr_string[i]
                if self._validate_eng_name(tempName):
                    eng_name = eng_name + tempName

            if len(eng_name):
                eng_name = eng_name.replace(',', ' ').replace('.', ' ').replace('/', ' ')

                name = eng_name.split(' ')

                if len(name):
                    self._last_name = re.sub('[^a-zA-Z ]', '', name[0].strip())
                    self._first_name = re.sub('[^a-zA-Z ]', '', ' '.join(name[1:]).strip())
        except Exception as e:
            logging.error('%s: Error when running function "%s", error = %s' % (self._vendor, sys._getframe().f_code.co_name, str(e)))


    def _get_macau_id(self, id_num):

        try:
            doc_num = id_num.replace('（', '(').replace('）', ')')
            doc_num = doc_num[-10:]
            doc_num_list = []
            doc_num_list.append(doc_num)
            doc_num = MRZOCRCleaner.apply(doc_num_list, formatType='MACID')
            doc_num = re.sub('[^0-9()]', '', ''.join(doc_num))

            if len(doc_num) == 10:
                return doc_num
            else:
                return ''
        except Exception as e:
            logging.error('%s: Error when running function "%s", error = %s' % (self._vendor, sys._getframe().f_code.co_name, str(e)))
            return ''

    '''
    ======================================
    澳门身份证，卡式
    ======================================
    '''
    def _recog_macau_id_old(self, ocr_string):

        try:
            logging.info('Tring to recognize as MACAU ID - OLD ...')

            self._country = 'CHN'

            # Extract Doc ID
            doc_num = ''.join(ocr_string[-1]).strip()
            self._doc_number = self._get_macau_id(doc_num)

            # Extract Name
            tempString = ''.join(re.findall(r"\d+", ocr_string[4])) + ''.join(re.findall(r"\d+", ocr_string[8]))
            self._local_name = self._convCTC2GBK(tempString)

            # Extract Sex
            sex_list = ['男M', '女F']
            sex_idx = -1
            for idx in range(len(ocr_string)):
                sex_cnt = 0
                for key in sex_list:
                    tempString = ocr_string[idx].upper()

                    if key in tempString:
                        sex_idx = idx
                        sex = re.sub('[^a-zA-Z]', '', tempString).upper()
                        sex = sex[-1]

                        if sex in ('F', 'M'):
                            self._sex = sex
                            break

            # Extract DOB and Expiry Date
            if sex_idx > 0:
                DOB = ''.join(re.findall(r"\d+", ocr_string[sex_idx - 2]))
                DOE = ''.join(re.findall(r"\d+", ocr_string[sex_idx + 4]))

                if self._check_date(DOB, '%d%m%Y'):
                    self._DOB = time.strftime('%Y-%m-%d', time.strptime(DOB, '%d%m%Y'))

                if self._check_date(DOE, '%d%m%Y'):
                    self._DOE = time.strftime('%Y-%m-%d', time.strptime(DOE, '%d%m%Y'))

                return True
            else:
                return False
        except Exception as e:
            logging.error('%s: Error when running function "%s", error = %s' % (self._vendor, sys._getframe().f_code.co_name, str(e)))
        finally:
            logging.info(self.to_dict())


    def _contain_zh(self, word):
        '''
        判断传入字符串是否包含中文
        :param word: 待判断字符串
        :return: True:包含中文  False:不包含中文
        '''
        try:
            zh_pattern = re.compile(u'[\u4e00-\u9fff]+')
            # word = word.decode()
            match = zh_pattern.search(word)

            return match
        except Exception as e:
            logging.error('%s: Error when running function "%s", error = %s' % (self._vendor, sys._getframe().f_code.co_name, str(e)))
            return False

    '''
    ======================================
    香港居民身份证号码校验
    ======================================
    '''
    def _validate_hk_id(self, id_number):
        """Verify function
        >>> _validate_hk_id('C123456(9)')
        True
        >>> _validate_hk_id('AY987654(A)')
        False
        """

        def char2digit(character):
            """Convert character to digit
            >>> char2digit('A')
            1
            >>> char2digit('Z')
            26
            >>> char2digit('1')
            1
            """
            if len(character) != 1:
                return None
            if character.isupper():
                return ord(character) - ord('A') + 1
            elif character.isdigit():
                return int(character)
            else:
                raise None

        def accumulate(reversed_number_list):
            """Accumulate
            >>> accumulate([6, 5, 4, 3, 2, 1, 7])
            133
            >>> accumulate([5, 5, 5, 5, 5, 5, 12])
            231
            """
            REVERSED_WEIGHT = [2, 3, 4, 5, 6, 7, 8, 9]
            accumulate = 0
            for idx in range(0, len(reversed_number_list)):
                accumulate += reversed_number_list[idx] * REVERSED_WEIGHT[idx]
            return accumulate

        FORMAT_REGEX = re.compile('(([A-Z]{1,2})([0-9]{6}))\(([0-9]|A)\)')

        matched = FORMAT_REGEX.search(id_number)
        if matched is None:
            return False
        matched_groups = matched.groups()
        character = matched_groups[1]
        digit = matched_groups[2]
        check_digit = matched_groups[3]
        reversed_number_list = []
        for item in reversed(list(character + digit)):
            reversed_number_list.append(char2digit(item))
        accumulate = accumulate(reversed_number_list)
        accumulate += int(check_digit, base=16)
        remainder = divmod(accumulate, 11)[1]
        return (remainder == 0)
