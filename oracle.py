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
    # Load all documents in the directory
    documents = read_all_documents_in_directory("./documents")

    # pdf_loader = PyPDFLoader("./docs_test/renova_devops_cronograma_atual.pdf")
    # csv_loader = CSVLoader(
    #     file_path="./docs_test/placas_video_grande_processadas.csv")
    # text_loader = TextLoader("./docs_test/links-gits-azure-devops.txt")

    # documents = []
    # for loader in [pdf_loader, csv_loader, text_loader]:
    #     documents.extend(loader.load())

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
    input_variables=["context", "input"],  # Changed "query" to "input"
    template="""
    Você é um assistente que responde perguntas com base nos documentos fornecidos.

    Documentos: {context}

    Pergunta: {input}

    Responda apenas com informações dos documentos acima. Se não puder encontrar uma resposta, diga: "A informação não está disponível nos documentos fornecidos."
    """
)

# Create the document chain
document_chain = create_stuff_documents_chain(llm, prompt_template)

# Debugging: Print the input schema of the document chain
print("Document Chain Input Schema:", document_chain.input_schema.schema())

# Debugging: Print the output schema of the document chain
print("Document Chain Output Schema:", document_chain.output_schema.schema())

# Create the retrieval chain
qa_chain = create_retrieval_chain(retriever, document_chain)

# Debugging: Print the input schema of the retrieval chain
print("QA Chain Input Schema:", qa_chain.input_schema.schema())

# Debugging: Print the output schema of the retrieval chain
print("QA Chain Output Schema:", qa_chain.output_schema.schema())

st.title("R-InsightDocs")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("You:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Debugging: Print the user input
    print("User Input:", user_input)

    # Invoke the retrieval chain
    response = qa_chain.invoke({"input": user_input})

    # Debugging: Print the full response from the retrieval chain
    print("Full Response from QA Chain:", response)

    # Extract the answer and source documents
    answer = response["answer"]
    source_documents = response["context"]

    # Debugging: Print the answer and source documents
    print("Answer:", answer)
    print("Source Documents:", source_documents)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

    # Display the source documents (optional)
    with st.expander("Documentos de origem"):
        for doc in source_documents:
            st.markdown(doc.page_content)
