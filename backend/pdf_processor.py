import os
from typing import List, Dict, Any
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create vector store directory if it doesn't exist
VECTOR_STORE_DIR = "vector_stores"
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.
    """
    logger.info(f"Extracting text from PDF: {pdf_path}")
    
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = pypdf.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise
    
    return text

def process_document(pdf_path: str, document_id: str) -> None:
    """
    Process a PDF document and create a vector store for it.
    """
    logger.info(f"Processing document: {document_id}")
    
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)
        
        # Create vector store using Google's embeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001"  # ✅ Corrected model name
        )

        vector_store = FAISS.from_texts(chunks, embeddings)

        # Save vector store
        vector_store_path = os.path.join(VECTOR_STORE_DIR, document_id)
        vector_store.save_local(vector_store_path)

        logger.info(f"Document processed successfully: {document_id}")
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise

def ask_question(pdf_path: str, question: str) -> str:
    """
    Answer a question based on the content of a PDF document.
    """
    document_id = os.path.basename(pdf_path).split('.')[0]
    vector_store_path = os.path.join(VECTOR_STORE_DIR, document_id)
    
    # Check if vector store exists, if not create it
    if not os.path.exists(vector_store_path):
        process_document(pdf_path, document_id)
    
    try:
        # Load vector store with Google's embeddings
        try:

            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/gemini-1.5-flash"  # ✅ Corrected model name
            )
        
            print("Embeddings model loaded successfully!")
        except Exception as e:
            print(f"Error: {e}")


        vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        
        # Create retriever
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )
        
        # Create QA chain with Google's Gemini model
        template = """
        You are an AI assistant that helps users understand PDF documents.
        Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """

        PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        chain_type_kwargs = {"prompt": PROMPT}
        
        # Use Gemini Pro model
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",  # ✅ Corrected model name
            temperature=0
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs=chain_type_kwargs,
            return_source_documents=False
        )
        
        # Get answer
        result = qa_chain.invoke({"query": question})
        return result["result"]
    
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        return f"I'm sorry, I encountered an error while processing your question: {str(e)}"
