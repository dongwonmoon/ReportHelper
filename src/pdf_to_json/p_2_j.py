import fitz
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import json
import os


def extract_text_from_pdf(pdf_path):
    pdf_data = {}
    text_found = False

    # 1. Try extracting text using PyMuPDF
    try:
        pdf_document = fitz.open(pdf_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text()
            if text.strip():  # If text is found
                pdf_data[f'page{page_num + 1}'] = text
                text_found = True
            else:
                pdf_data[f'page{page_num + 1}'] = None  # Placeholder for text extraction failure
        pdf_document.close()
    except Exception as e:
        print(f"PyMuPDF extraction failed: {e}")

    # 2. If no text found or if text extraction failed, use pdfplumber and OCR
    if not text_found:
        try:
            images = convert_from_path(pdf_path)
            for page_num, image in enumerate(images):
                text = pytesseract.image_to_string(image, lang='kor')
                if text.strip():  # If OCR text is found
                    pdf_data[f'page{page_num + 1}'] = text
                else:
                    pdf_data[f'page{page_num + 1}'] = "No text found"
        except Exception as e:
            print(f"OCR extraction failed: {e}")

    return pdf_data

def save_as_json(data, json_path):
    try:
        # 파일 열기
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print("Data successfully written to JSON.")
    except Exception as e:
        print(f"Error: {e}")

pdf_path = 'ReportHelper/data/pdf/'
json_path = 'ReportHelper/data/json/'
pdf_list = os.listdir(pdf_path)
for pdf_file in pdf_list:
    pdf_data = extract_text_from_pdf(pdf_path+pdf_file)
    json_file = pdf_file[:-3] + 'json'
    save_as_json(pdf_data, json_path+json_file)