import os
import subprocess
from dotenv import load_dotenv
load_dotenv()

from langchain_chroma import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_groq import ChatGroq
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import StructuredQueryOutputParser, get_query_constructor_prompt
from langchain.retrievers.self_query.chroma import ChromaTranslator
from pydantic_classes import sentiment, complaint_summary
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ['GOOGLE_API_KEY'] = os.getenv("GEMINI_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_FLASH"))
embed_model = OllamaEmbeddings(model=os.getenv("OLLAMA_EMBED"))
llama = ChatGroq(model=os.getenv("LLAMA_70B_GROQ"))

def get_recommended_products(query: str) -> str:
    vector_store = Chroma(persist_directory='chroma/sephora_store_db', embedding_function=embed_model)

    metadata_field_info = [
        AttributeInfo(
            name='brand',
            description="The brand of the product. Examples include 'sephora collection', 'Fenty Beauty' etc",
            type="string"
        ),
        AttributeInfo(
            name='category',
            description="T  he category of the product such as 'skincare', 'makeup', 'hair' etc",
            type="string"
        ),
        AttributeInfo(
            name='price',
            description="The price of the product in USD",
            type="float"
        ),
        AttributeInfo(
            name='rating',
            description="The average user rating for a product from a sacle of 1 to 5",
            type="float"
        ),
        AttributeInfo(
            name='number_of_reviews',
            description="The total number of reviews given to a product",
            type="integer"
        ),
    ]

    document_content_description = "Combined  textual description of the product. Including ingredients and product details"

    prompt = get_query_constructor_prompt(document_content_description, metadata_field_info)
    output_parser = StructuredQueryOutputParser.from_components()
    query_constructor = prompt | llama | output_parser

    retriever = SelfQueryRetriever(
        query_constructor=query_constructor,
        vectorstore=vector_store,
        structured_query_translator=ChromaTranslator()
    )

    res = retriever.invoke(query)

    return str(res)


def analyse_sentiment(email_body: str):
    parser = JsonOutputParser(pydantic_object=sentiment)
    with open("prompt_templates/sentiment_analysis.txt", "r") as f:
        prompt_body = f.read()
    
    prompt = PromptTemplate(template=prompt_body,
                            input_variables=["email"],
                            partial_variables={"format_instructions":parser.get_format_instructions()},)

    chain = prompt | llm | parser

    result = chain.invoke({"email": email_body})

    return result['sentiment_type']

def get_complaint_summary(email_body: str):
    parser = JsonOutputParser(pydantic_object= complaint_summary)
    with open("prompt_templates/complaint_summary.txt", "r") as f:
        prompt_body = f.read()
    
    prompt = PromptTemplate(template=prompt_body,
                            input_variables=["email"],
                            partial_variables={"format_instructions":parser.get_format_instructions()},)

    chain = prompt | llm | parser

    result = chain.invoke({"email": email_body})

    return result['summary']