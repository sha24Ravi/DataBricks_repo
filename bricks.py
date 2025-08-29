from databricks import sql
from langchain_text_splitters import TokenTextSplitter
from langchain_community.embeddings import GPT4AllEmbeddings
from mistralai import Mistral
import numpy as np
import faiss
from openai import OpenAI
import streamlit as st
import os

access_token = os.getenv("DATABRICKS_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

def establish_databricks_conect():
   connection = sql.connect(
                        server_hostname = access_token,
                        http_path = "/sql/1.0/warehouses/",
                        access_token = access_token)
 
   return connection.cursor()

def fetch_data(cursor):
   cursor.execute("SELECT * FROM workspace.db.customer_churn_dataset_training_master limit 30")
   return cursor.fetchall()


def transform_fetched_data(results):
   chunks = []

   for row in results:
       chunk_text = (
        f"CustomerID: {row.CustomerID}, Age: {row.Age}, Gender: {row.Gender}, "
        f"Tenure: {row.Tenure}, Usage Frequency: {row['Usage Frequency']}, Support Calls: {row['Support Calls']}, "
        f"Payment Delay: {row['Payment Delay']}, Subscription Type: {row['Subscription Type']}, "
        f"Contract Length: {row['Contract Length']}, Total Spend: {row['Total Spend']}, "
        f"Last Interaction: {row['Last Interaction']}, Churn: {row.Churn}, "
        f"Tenure Category: {row.tenure_category}, Delayed Payment Flag: {row.Delayed_Payment_Flag}"
      )
       chunks.append(chunk_text)
   combined_text = "\n\n".join(chunks)
   return combined_text
   

def text_split(combined_text):
   text_splitter=TokenTextSplitter(
    encoding_name="cl100k_base", 
    chunk_size=500,
    chunk_overlap=50,
    )
   chunks = text_splitter.split_text(combined_text)
   print(chunks)
   return chunks

@st.cache_data
def intiate_prompt(user_input):
   cur= establish_databricks_conect()
   results =fetch_data(cur) 
   combine_text=transform_fetched_data(results)
   chunks=text_split(combine_text)

   gpt4all_embd = GPT4AllEmbeddings()
   text_embeddings = np.array([gpt4all_embd.embed_query(chunk) for chunk in chunks])
   d = text_embeddings.shape[1]
   index = faiss.IndexFlatL2(d)
   index.add(text_embeddings)

   question = "how many customers are there?"
   question_embeddings = np.array([gpt4all_embd.embed_query(user_input)])
   print(user_input)
   D, I = index.search(question_embeddings, k=2) # distance, index
   retrieved_chunk = [chunks[i] for i in I.tolist()[0]]
   prompt = f"""
   Context information is below.
    ---------------------
    {retrieved_chunk}
    ---------------------
Given the context information and not prior knowledge, answer the query.
Query: {user_input}
Answer:
"""
   client = OpenAI(
   api_key=openai_api_key
   )
   messages = [
        
           {"role": "user", "content": prompt}
        
    ]
   response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    store=True,
   )
   print(response)
   return response.choices[0].message.content







   
