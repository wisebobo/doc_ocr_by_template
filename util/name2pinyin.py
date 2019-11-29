# -*- coding:utf-8 -*-
import pypinyin

# 不带声调的(style=pypinyin.NORMAL)
def pinyin(word):
    s = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        s += ''.join(i)
    return s.upper()

# 带声调的(默认)
def yinjie(word):
    s = ''
    # heteronym=True开启多音字
    for i in pypinyin.pinyin(word, heteronym=True):
        s = s + ''.join(i) + " "
    return s.upper()

def ChineseName(name):

	if name[0:2] in ('欧阳', '司马', '上官', '西门'):
		local_last_name = name[0:2]
		local_first_name = name[2:]
	else:
		local_last_name = name[0]
		local_first_name = name[1:]

	last_name = pinyin(local_last_name)
	first_name = pinyin(local_first_name)

	return last_name, first_name