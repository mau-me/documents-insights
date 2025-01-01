import streamlit as st
from dotenv import load_dotenv
import os
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from database import create_connection, check_user, initialize_database

# Inicializar o banco de dados
initialize_database()

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Read All Documents in the Directory


def read_all_documents_in_directory(directory):
    documents = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            loaded_docs = loader.load()
            documents.extend(loaded_docs)
        elif filename.endswith(".csv"):
            loader = CSVLoader(file_path)
            loaded_docs = loader.load()
            documents.extend(loaded_docs)
        elif filename.endswith(".txt"):
            loader = TextLoader(file_path)
            loaded_docs = loader.load()
            documents.extend(loaded_docs)
    return documents


@st.cache_resource
def load_documents():
    documents = read_all_documents_in_directory("./documents")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore.as_retriever()


retriever = load_documents()

# Initialize ChatGPT model
llm = ChatOpenAI(model="gpt-4", openai_api_key=openai_api_key, temperature=0)

# Define prompt template
prompt_template = PromptTemplate(
    input_variables=["context", "input"],
    template="""
    Você é um assistente que responde perguntas com base nos documentos fornecidos.
    Responda às perguntas como se fosse um baiano.

    Documentos: {context}

    Pergunta: {input}

    Responda apenas com informações dos documentos acima. Se não puder encontrar uma resposta, diga: "A informação não está disponível nos documentos fornecidos."
    """
)

# Create the document chain
document_chain = create_stuff_documents_chain(llm, prompt_template)

# Create the retrieval chain
qa_chain = create_retrieval_chain(retriever, document_chain)

# Login functionality


def login_page():
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Login"):
        conn = create_connection()
        if check_user(conn, username, password):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")
        conn.close()

# Chatbot page


def chatbot_page():
    st.title("R-InsightDocs")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("You:"):
        st.session_state.messages.append(
            {"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        response = qa_chain.invoke({"input": user_input})
        answer = response["answer"]
        source_documents = response["context"]

        st.session_state.messages.append(
            {"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

        with st.expander("Documentos de origem"):
            for doc in source_documents:
                st.markdown(doc.page_content)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Main function


def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        chatbot_page()
    else:
        login_page()


if __name__ == "__main__":
    main()
