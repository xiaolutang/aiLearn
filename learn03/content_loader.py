# content_loader.py
import os

from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from learn03.document_spilt import markdown_file_load_and_document_spilt


def load_document():
    plan_documents = markdown_file_load_and_document_spilt("../plan.md")
    print(f"Total characters: {len(plan_documents[0].page_content)} ${plan_documents[-1].page_content}")
    learn_documents = markdown_file_load_and_document_spilt("../README.md")
    # 两个文档的数据进行结合
    plan_documents.extend(learn_documents),
    # 嵌入
    embeddings = DashScopeEmbeddings(model="text-embedding-v1",dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"))
    db = Chroma.from_documents(documents=plan_documents, embedding=embeddings, persist_directory="./chroma_db")

def search(query:str)-> list[Document]:
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=DashScopeEmbeddings(model="text-embedding-v1"))
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    return retriever.invoke(query)
