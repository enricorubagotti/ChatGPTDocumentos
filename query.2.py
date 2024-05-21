#!pip install streamlit
#!pip install openai
import streamlit as st
import pdfplumber
import openai
import os
import time

# Set your OpenAI API key
openai.api_key = os.getenv('openai_api_key')

def query_openai(prompt):
    retries = 5
    for i in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Adjust the model name if necessary
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=300  # Adjust this value as needed
            )
            return response
        except openai.error.RateLimitError as e:
            wait_time = 2 ** i  # Exponential backoff
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"An error occurred: {e}")
            break

st.title("PDF Question Answering with OpenAI")

uploaded_file_1 = st.file_uploader("Choose the first PDF file", type="pdf")
uploaded_file_2 = st.file_uploader("Choose the second PDF file", type="pdf")

if uploaded_file_1 is not None and uploaded_file_2 is not None:
    text_1, text_2 = '', ''
    
    with pdfplumber.open(uploaded_file_1) as pdf:
        for page in pdf.pages:
            text_1 += page.extract_text()
    
    with pdfplumber.open(uploaded_file_2) as pdf:
        for page in pdf.pages:
            text_2 += page.extract_text()
    
    st.text_area("Extracted Text from First PDF", text_1)
    st.text_area("Extracted Text from Second PDF", text_2)

    question = st.text_input("Ask a question:")

    if st.button("Submit"):
        if question:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Adjust the model name if necessary
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": f"Document 1: {text_1}\n\nDocument 2: {text_2}\n\nQuestion: {question}\nAnswer:"}],
                temperature=0,
                max_tokens=300  # Adjust this value as needed
            )
            answer = response['choices'][0]['message']['content'].strip()
            token_usage = response['usage']['total_tokens']
            st.write(f"Answer: {answer}")
            st.write(f"Tokens used: {token_usage}")
        else:
            st.warning("Please enter a question.")
else:
    st.warning("Please upload two PDF files.")
