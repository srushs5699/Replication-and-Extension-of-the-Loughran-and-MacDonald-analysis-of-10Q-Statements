import csv
import re
import os
from collections import Counter
import numpy as np


def load_master_dictionary(file_path):
    dictionary = {}
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            word = row['Word'].upper()
            dictionary[word] = {
                'Sequence Number': row['Sequence Number'],
                'Word Count': row['Word Count'],
                'Negative': row['Negative'],
                'Positive': row['Positive'],
            }
    return dictionary


def clean_text(text):

    text = re.sub(r'<.*?>', '', text)

    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    return text


def count_word_frequencies(text, lm_dictionary):
    cleaned_text = clean_text(text).upper()
    words = cleaned_text.split()

    word_count = Counter(words)
    frequencies = {word: word_count[word] for word in lm_dictionary if word in word_count}

    return frequencies


def process_all_files_in_directory(lm_dictionary, cleaned_dir):
    # Initialize variables
    word_list = [word for word in lm_dictionary]
    num_docs = len([f for f in os.listdir(cleaned_dir) if f.endswith('.txt')])
    num_words = len(word_list)

    # Create empty matrices
    tf_matrix = np.zeros((num_docs, num_words))
    idf_matrix = np.zeros((num_docs, num_words))
    doc_length_matrix = np.zeros((num_docs, 1))

    doc_index = 0

    # Process each file in the directory
    for filename in os.listdir(cleaned_dir):
        if filename.endswith('.txt'):
            file_path = os.path.join(cleaned_dir, filename)

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                mda_content = f.read()

            word_frequencies = count_word_frequencies(mda_content, lm_dictionary)
            total_words = sum(word_frequencies.values())

            # Update document length matrix
            doc_length_matrix[doc_index, 0] = total_words

            # Update tf and idf matrices
            for word, freq in word_frequencies.items():
                word_index = word_list.index(word)
                tf_matrix[doc_index, word_index] = freq
                idf_matrix[doc_index, word_index] = 1  # The word appeared in this document

            doc_index += 1

    # Calculate IDF (log(N / (1 + df)))
    doc_freq = np.sum(idf_matrix, axis=0)
    idf_values = np.log(num_docs / (1 + doc_freq))

    # Apply IDF to the tf matrix to get tf-idf
    tfidf_matrix = tf_matrix * idf_values

    return tfidf_matrix, doc_length_matrix, tf_matrix, idf_matrix


def calculate_tfidf_weight(tf_matrix, idf_matrix, doc_length_matrix):
    # Normalize tf by document length
    term_weight = tf_matrix / doc_length_matrix

    return term_weight


# Load the dictionary
lm_dictionary = load_master_dictionary('LoughranMcDonald_MasterDictionary_2018.csv')

# Specify directories
cleaned_dir = './cleaned'

# Process files and get matrices
tfidf_matrix, doc_length_matrix, tf_matrix, idf_matrix = process_all_files_in_directory(lm_dictionary, cleaned_dir)

# Calculate term weights
term_weight = calculate_tfidf_weight(tf_matrix, idf_matrix, doc_length_matrix)

# tfidf_matrix and term_weight are now ready for regression or other analysis
