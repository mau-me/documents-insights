import streamlit as st
from dotenv import load_dotenv
import os
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Function to load and process documents


@st.cache_resource
def load_documents():
    # Example: Add support for multiple formats
    pdf_loader = PyPDFLoader("./docs_test/renova_devops_cronograma_atual.pdf")
    csv_loader = CSVLoader(
        file_path="./docs_test/placas_video_grande_processadas.csv")
    text_loader = TextLoader("./docs_test/links-gits-azure-devops.txt")

    documents = []
    for loader in [pdf_loader, csv_loader, text_loader]:
        documents.extend(loader.load())

    # Split documents into smaller chunks for embeddings
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    # Generate embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever()
    return retriever


retriever = load_documents()

# Initialize ChatGPT model
llm = ChatOpenAI(model="gpt-4", openai_api_key=openai_api_key)

# Define RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

st.title("R-InsightDocs")

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("You:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response = qa_chain({"query": user_input})
    answer = response["result"]

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
