# Document OCR by template
This is an OCR program designed for travel document. It can now support 23 types of documents with pre-defined template. You can add whatever you like.

0. Passport
1. China ID card
2. HK ID card (new format)
3. HK ID card (old format)
4. Macau ID card (new format)
5. Macau ID card (old format)
6. Macau ID card - backside with MRZ
7. China to HK/Macau Entry Permit card
8. China to HK/Macau Entry Permit (Old)
9. China to Taiwan Entry Permit card
10. HK/Macau to China Entry Permit card
11. HK/Macau to China Entry Permit card (Old)
12. Taiwan to China Entry Permit card
13. Taiwan to China Entry Permit (Old)
14. Australia Driver Licence - New South Wales
15. Australia Driver Licence - Victoria
16. Australia Driver Licence - Capital Territory
17. Australia Driver Licence - Queensland
18. Australia Driver Licence - Western
19. Australia Driver Licence - Northern Territory
20. Australia Driver Licence - Tasmania
21. Australia Driver Licence - South Australia
22. New Zealand Driver Licence


## Environment
- CentOS / Windows
- python 3.7+

## Installation
```
git clone --recursive https://github.com/wisebobo/doc_ocr_by_template
cd doc_ocr_by_template
pip3 install -r requirements.txt
```

## How to use?
Go to project folder, edit the settings.py to update those APP_ID/APP_KEY to your own one.

Then execute
```
./startServer.sh

or

python3 startServer.py
```
![Image text](https://github.com/wisebobo/doc_ocr_by_template/raw/master/intro/Sample01.jpg)

## Design Concept
1. Running tornado for exposing API service
2. After receiving base64 image, pass to a pre-trained ResNet50 model for image classification to retrieve the document type.
3. After getting the document type, create multiple threads to call Tencent/Baidu/Face++/Netease/JD OCR API to retrieve the 1st round of OCR result
4. Base on the 1st round of OCR result, to match against the pre-defined template. Template is created by using the [project folder]/templates/template_generator.html. If template match, crop the recognition area to a new image (idea is to remove those unnecessary information to get a more accurate OCR result), then pass to Tencent/Baidu/Face++/Netease/JD OCR API again.
5. Match the 2nd OCR result against the template fields
6. According to corresponding document type to apply respective data cleasing logic
7. Calculate the score

## Reference
1. MRZ https://github.com/konstantint/PassportEye
