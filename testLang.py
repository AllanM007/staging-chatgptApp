import os
import requests
import openai
import pinecone
from pathlib import Path
from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
import gradio as gr

# Setup Pinecone API key as an environment variable.
api_key = "fa3b0ae2-aa28-43c4-9f57-1071217725e7"
environment = "asia-southeast1-gcp-free"

os.environ["PINECONE_API_KEY"] = api_key

# Set your OpenAI API key as an environment variable.
os.environ["OPENAI_API_KEY"] = "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"
# openai.organization = "your-org-here"

openai.api_key = os.getenv("OPENAI_API_KEY")

from llama_index.vector_stores import PineconeVectorStore
from llama_index.storage.storage_context import StorageContext
from llama_index import (
    GPTVectorStoreIndex,
    LLMPredictor,
    ServiceContext,
    PromptHelper,
    load_index_from_storage,
    download_loader,
    VectorStoreIndex,
    SimpleDirectoryReader,
)

index_name = "mombo-stadi"

pinecone.init(api_key=api_key, environment=environment)

if index_name not in pinecone.list_indexes():
    pinecone.create_index(name=index_name, dimension=1536, metric="cosine")

index = pinecone.Index(index_name)


file_names = os.listdir("./content/")

# Dictionary to store the indices
indices_dict = {}

for file_name in file_names:
    print(file_name)
    # Get the document ID by removing the file extension
    document_id = os.path.splitext(file_name)[0]
    # Use document_id as Pinecone title
    pinecone_title = document_id

    metadata_filters = {
        "name": document_id
    }  # Replace with appropriate metadata filters
    vector_store = PineconeVectorStore(
        index_name=index_name,
        environment=environment,
        metadata_filters=metadata_filters,
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

file_paths = Path("./content/")
pdf_paths = Path(file_paths).glob("*.pdf")
for pdf_path in pdf_paths:
    print(pdf_path)
    try:
        # In this particuler case we Load data from a directory containing pdf files, So we used the PDFReader loader.
        PDFReader = download_loader("PDFReader")
        loader = PDFReader()
        aa_docs = loader.load_data(file=pdf_path)
        print(f"Loaded document from {pdf_path}")
    except Exception as e:
        # Skips any files that may cause error while loading.
        print(f"Error reading PDF file: {pdf_path}. Skipping... Error: {e}")

        # Create the GPTVectorStoreIndex from the documents
        indices_dict[document_id] = GPTVectorStoreIndex.from_documents(
            aa_docs, storage_context=storage_context
        )
        indices_dict[document_id].index_struct.index_id = pinecone_title


# This will allow to query a response without having to load files repeatedly.
def data_querying(input_text):
    # We Must reinitialize Pinecone in oder to load our previously created index.
    api_key = "fa3b0ae2-aa28-43c4-9f57-1071217725e7"
    environment = "asia-southeast1-gcp-free"

    os.environ["PINECONE_API_KEY"] = api_key

    index_name = "mombo-stadi"
    pinecone.init(api_key=api_key, environment=environment)

    model_name = "text-embedding-ada-002"

    embed = OpenAIEmbeddings(
        model=model_name,
        openai_api_key="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",
    )
    # This text field represents the field that the text contents of your document are stored in
    text_field = "text"

    # load pinecone index for langchain
    index = pinecone.Index(index_name)

    vectorstore = Pinecone(index, embed.embed_query, text_field)
    # Query the vectorized data
    vectorstore.similarity_search(
        input_text, k=3  # our search query  # return 3 most relevant docs
    )
    # Using LangChain we pass in our model for text generation.
    llm = ChatOpenAI(temperature=0.2, model_name="gpt-3.5-turbo", max_tokens=512)
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())
    # Finally we return the result of the search query.
    result = qa.run(input_text)
    print(result)
    response = result

    return response


# Create your gradio Interface
iface = gr.Interface(
    fn=data_querying,
    inputs=gr.inputs.Textbox(lines=7, label="Enter your text"),
    outputs="text",
    title="Test Model RENE",
)
iface.launch(share=True)
