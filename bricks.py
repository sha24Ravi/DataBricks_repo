from databricks import sql
from langchain_text_splitters import TokenTextSplitter
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chat_models import openai
from langchain.chains import LLMChain
import numpy as np
import faiss
from openai import OpenAI
import streamlit as st
import os
from langchain.chains import RetrievalQA
access_token = os.getenv("DATABRICKS_TOKEN")
openai_key = ""



def transform_fetched_data(df):

   relevant_cols = ["CustomerID", "Churn", "Revenue", "PlanType", "Usage"]
   df_reduced = df[relevant_cols]

   chunk_size=20

   chunks= [df_reduced.iloc[i:i+chunk_size] for i in range(0, len(df), chunk_size)]
   chunk_text= [chunk.to_dict(orient="records") for chunk in chunks]
   chunk_texts_str = [str(chunk) for chunk in chunk_text]
   print(chunk_texts_str)
   return chunk_texts_str
   
def embedings_store(chunks_texts_str):
    embedding=OpenAIEmbeddings(api_key=openai_key)  
    vector_db=Chroma.from_texts(chunks_texts_str,embedding)
    vector_db.persist()
    return vector_db





def intiate_prompt(df,user_input):
   # cur= establish_databricks_conect()
   # results =fetch_data(cur) 
   llm = openai.ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=openai_key)

   columns = ", ".join(df.columns)

   prompt_template = PromptTemplate(
    input_variables=["question", "columns"],
    template="""
You are a Python assistant.
I have a pandas DataFrame `df` with the following columns:
{columns}

Generate a Python pandas expression to answer this question:
{question}

- Do not execute the code.
- Only return valid pandas code.
- Use the variable name df.
"""
)

   chain = LLMChain(llm=llm, prompt=prompt_template)

   
   generated_code = chain.run(question=user_input, columns=columns)
   extracted_data = eval(generated_code)
   print("Generated pandas code:")
   print(generated_code)
   return extracted_data

    
  







   
