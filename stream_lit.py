
import streamlit as st  
import base64
from bricks import intiate_prompt
import pandas as pd 
import os
import requests
from databricks.sdk import WorkspaceClient
from azure.storage.blob import BlobServiceClient


st.title("Upload your churn CSV file")
show_drop_down=0
account_name = "databricksetl24"
container_name = "dbcsv1"
sas_token = ""  # Do NOT include leading '?'
sas_container_token=""
    # Create the BlobServiceClient with SAS token
blob_service_client = BlobServiceClient(
          account_url=f"https://{account_name}.blob.core.windows.net",
        credential=sas_token
    )
container_client = blob_service_client.get_container_client(container_name)
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
blob_list = list(container_client.list_blobs())

if(len(blob_list)>0 and show_drop_down!=1):  
      file_names = [blob.name for blob in blob_list]
      st.title("files uploaded")
      selected_file = st.selectbox("Select a file", ["--Select a file--"] + file_names)

      

if uploaded_file is not None and show_drop_down!=1 :
    # Read CSV to DataFrame
   
    print(blob_service_client)
    # Get container client


    # Upload file from Streamlit file-like object
    blob_name = uploaded_file.name  # You can change the name if needed
    container_client.upload_blob(name=blob_name, data=uploaded_file, overwrite=True)

    st.success(f"✅ File '{blob_name}' uploaded to container '{container_name}'!")


def start_chart(df):
   st.title("Chat with GPT")

# Store chat history in session state
   if "messages" not in st.session_state:
    st.session_state.messages = []

# User input
   user_input = st.text_input("You:", "")

   if user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Call OpenAI chat completions
    response = intiate_prompt(df,user_input)

    # Get assistant message
    
    st.session_state.messages.append({"role": "assistant", "content": response})


    for msg in st.session_state.messages:
     if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Assistant:** {msg['content']}")   


if selected_file !="--Select a file--":
   file_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{selected_file}?{sas_container_token}"
   show_drop_down=1
   df = pd.read_csv(file_url)
   start_chart(df)
       