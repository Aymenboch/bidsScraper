import subprocess
import os
import json 
from flask_cors import CORS
from flask import Flask, send_file, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from nltk.corpus import stopwords
from keywords import keywords as consulting_keywords  

app = Flask(__name__)
#security
#CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
CORS(app)

@app.route('/run-scriptwb', methods=['POST'])
def run_spider_wb():
    try:
        number = request.json.get('number')
        region = request.json.get('region')
        print(number)
        print(region)
        command = ['scrapy', 'crawl', 'worldbank', '-o', 'output.csv', '-a', f'number={number}']
        working_dir = 'C:/Users/aayme/Desktop/kpmg/procurement_project'
        result = subprocess.run(command, cwd=working_dir, capture_output=True, text=True)

        if result.returncode == 0:
            processed_file = process_csv(f"{working_dir}/output.csv", region)
            if isinstance(processed_file, str) and processed_file.endswith('.xlsx'):
                return send_file(processed_file, as_attachment=True)
            else:
                return jsonify({"status": "error", "message": processed_file}), 500
        else:
            return jsonify({"status": "error", "message": result.stderr}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/download-excel/<value>', methods=['GET'])
def download_csv(value):
    print(value)
    if value == 'wb':
        file_path = 'C:/Users/aayme/Desktop/kpmg/results/worldbank.xlsx'
    else:
        file_path = 'C:/Users/aayme/Desktop/kpmg/procurement_project/ungm.xlsx'

    if os.path.exists(file_path):
        try:
            return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "File not found"}), 404
    
@app.route('/run-scriptungm', methods=['POST'])
def run_spider_ungm():
    numbers = request.json.get('selectedNumbers', [])
    region = request.json.get('region')
    print("Received numbers:", numbers)
    print("Region:", region)
    command = ['scrapy', 'crawl', 'ungm_spider', '-a', f'numbers={json.dumps(numbers)}' , '-a', f'region={json.dumps(region)}' ]
    working_dir = 'C:/Users/aayme/Desktop/kpmg/procurement_project'
    try:
        result = subprocess.run(command, cwd=working_dir, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            file_path = 'C:/Users/aayme/Desktop/kpmg/procurement_project/ungm.xlsx'
            return send_file(file_path, as_attachment=True, download_name='ungm.xlsx')
        else:
            return jsonify({"status": "error", "message": result.stderr}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


    
def process_csv(file_path, region):
    try:
        # Load the CSV into a DataFrame
        df = pd.read_csv(file_path, dtype={'link': str})
        print("DataFrame loaded, first few rows:\n", df.head())
        print("DataFrame shape:", df.shape)
        print("Columns:", df.columns)
        df['link'] = df['link'].apply(lambda x: x[:-10] + x[-10:].upper())
        # Normalize and clean data
        df['notice_type'] = df['notice_type'].str.strip().str.capitalize()
        df['region'] = df['region'].str.strip().str.capitalize()
        df['bid_description'] = df['bid_description'].fillna('').str.strip()

        # Setup stopwords
        stop_words = stopwords.words('english') + \
                     stopwords.words('spanish') + \
                     stopwords.words('portuguese') + \
                     stopwords.words('french')
        print("Number of stopwords:", len(stop_words))

        # Setup the TF-IDF Vectorizer
        vocabulary = {key.lower(): idx for idx, key in enumerate(consulting_keywords)}
        print("Vocabulary size:", len(vocabulary))
        
        tfidf = TfidfVectorizer(stop_words=stop_words, ngram_range=(1, 3), vocabulary=vocabulary, lowercase=False)
        descriptions = df['bid_description'].values
        tfidf_matrix = tfidf.fit_transform(descriptions)
        print("TF-IDF matrix shape:", tfidf_matrix.shape)
        print("Sample TF-IDF values for first document:", tfidf_matrix[0].toarray())

        # Filter data based on TF-IDF scores
        consulting_mask = tfidf_matrix.sum(axis=1).A.flatten() > 0.2
        filtered_df = df[consulting_mask]
        print("Entries above TF-IDF threshold:", np.sum(consulting_mask))
        print("Shape after TF-IDF filtering:", filtered_df.shape)

        # Define notice types and filter
        notice_types = [
            'Request for expression of interest',
            'Invitation for bids',
            'General procurement notice',
            'Invitation for prequalification'
        ]
        filtered_df = filtered_df[filtered_df['notice_type'].isin(notice_types)]
        print("Shape after notice type filtering:", filtered_df.shape)

        # Filter by region containing 'Africa'
        filtered_df = filtered_df[filtered_df['region'].str.contains(region, case=False, na=False)]
        print("Shape after region filtering:", filtered_df.shape)

        # Exclude entries with 'non-consulting' in 'bid_description'
        filtered_df = filtered_df[~filtered_df['bid_description'].str.contains('non-consulting', case=False, na=False)]
        print("Shape after excluding 'non-consulting':", filtered_df.shape)

        # Save to Excel
        excel_path = 'C:/Users/aayme/Desktop/kpmg/results/worldbank.xlsx'
        filtered_df.to_excel(excel_path, index=False, engine='openpyxl')
        print("Excel file saved to:", excel_path)

        return excel_path
    except Exception as e:
        print("Error in process_csv:", str(e))
        return str(e)
 
if __name__ == '__main__':
    app.run(debug=True)
