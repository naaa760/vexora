import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Apply custom styling and animations
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;700&display=swap');

        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(to right, #3E2723, #FFECB3);
            color: white;
        }
        
        .stApp {
            background: linear-gradient(to right, #3E2723, #FFECB3);
        }
        
        .stTitle {
            text-align: center;
            font-size: 3em;
            font-weight: bold;
            color: #FFCC80;
            animation: fadeIn 2s ease-in-out;
        }
        
        .stTextInput, .stButton, .stExpander {
            background-color: #5D4037;
            color: #FFECB3;
            border-radius: 10px;
            padding: 10px;
            font-size: 16px;
            transition: all 0.3s ease-in-out;
        }

        .stButton:hover {
            background-color: #8D6E63;
            transform: scale(1.05);
            color: white;
        }

        .stExpander:hover {
            background-color: #6D4C41;
        }

        .fade-in {
            animation: fadeIn 1.5s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .sidebar-header {
            font-size: 20px;
            font-weight: bold;
            color: #FFCC80;
            margin-bottom: 10px;
            text-align: center;
        }

    </style>
    """,
    unsafe_allow_html=True,
)

# Page Title with animation
st.markdown('<h1 class="stTitle fade-in">📜 Gemma Model Document Q&A</h1>', unsafe_allow_html=True)

# LLM Model
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Gemma2-9b-it")

# Define Prompt
prompt = ChatPromptTemplate.from_template(
    """
    Answer the questions based on the provided context only.
    Please provide the most accurate response based on the question.
    <context>
    {context}
    <context>
    Question: {input}
    """
)

# Vector Embedding Function
def vector_embedding():
    if "vectors" not in st.session_state:
        with st.spinner("🔄 Processing Documents... Please wait!"):
            st.session_state.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            st.session_state.loader = PyPDFDirectoryLoader("./us_census")  # Data Ingestion
            st.session_state.docs = st.session_state.loader.load()  # Document Loading
            st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs[:20])  # Splitting
            st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)  # Vector embeddings
        st.success("✅ Vector Store DB is ready!")

# Sidebar with animation
with st.sidebar:
    st.markdown('<div class="sidebar-header">🔧 Settings</div>', unsafe_allow_html=True)
    if st.button("🔄 Embed Documents", key="embed_docs"):
        vector_embedding()

# User Input
prompt1 = st.text_input("💡 Enter Your Question About the Documents", key="user_input", help="Type your query here...")

# Processing and Response
if prompt1:
    with st.spinner("🤖 Generating Answer... Please wait!"):
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = st.session_state.vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        start_time = time.process_time()
        response = retrieval_chain.invoke({"input": prompt1})
        elapsed_time = time.process_time() - start_time

    # Display response with animation
    st.success(f"🎯 Answer: {response['answer']}")
    st.write(f"⏳ Response Time: {elapsed_time:.2f} seconds")

    # Document Similarity Search with animated reveal
    with st.expander("🔍 Document Similarity Search", expanded=False):
        st.write("Here are the most relevant document chunks:")
        for i, doc in enumerate(response["context"]):
            st.markdown(f"<div class='fade-in'>📄 **Document {i+1}:**</div>", unsafe_allow_html=True)
            st.write(doc.page_content)
            st.write("🔹" * 10)
