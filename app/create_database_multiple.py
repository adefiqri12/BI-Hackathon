# from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders.pdf import PyMuPDFLoader
from langchain.document_loaders.xml import UnstructuredXMLLoader
from langchain.document_loaders import UnstructuredFileLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import openai
from dotenv import load_dotenv
import os
import shutil

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
# ---- Set OpenAI API key
# Change environment variable name from "OPENAI_API_KEY" to the name given in
# your .env file.
openai.api_key = os.environ["OPENAI_API_KEY"]

CHROMA_PATH = "chroma"
DATA_PATH = "data/books"


def main():
    generate_data_store()


loaders = {
    ".pdf": PyMuPDFLoader,
    ".xml": UnstructuredXMLLoader,
    ".csv": CSVLoader,
    ".txt": UnstructuredFileLoader,
}


def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def create_directory_loader(file_type, directory_path, encoding="utf-8"):
    loader_cls = loaders[file_type]
    loader_kwargs = {"encoding": encoding} if file_type == ".csv" else {}
    return DirectoryLoader(
        path=directory_path,
        glob=f"**/*{file_type}",
        loader_cls=loader_cls,  # Pass the loader class itself, not an instance
        loader_kwargs=loader_kwargs,
    )


def load_documents():
    document_list = []
    directory_path = "BI-Hackathon"

    for file_type in loaders:
        loader = create_directory_loader(
            file_type,
            directory_path,
            encoding="latin1" if file_type == ".csv" else "utf-8",
        )
        try:
            documents = loader.load()
            document_list.extend(documents)
        except UnicodeDecodeError as e:
            print(f"Encoding error loading {file_type} files: {e}")
        except Exception as e:
            print(f"Error loading {file_type} files: {e}")

    return document_list


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # Optional: Print a specific chunk for debugging
    if len(chunks) > 10:
        document = chunks[10]
        print(document.page_content)
        print(document.metadata)

    return chunks


def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")


if __name__ == "__main__":
    main()
