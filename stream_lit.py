
import streamlit as st  
import base64
from bricks import intiate_prompt


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
    response = intiate_prompt(user_input)

    # Get assistant message
    
    st.session_state.messages.append({"role": "assistant", "content": response})


    for msg in st.session_state.messages:
     if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Assistant:** {msg['content']}")   