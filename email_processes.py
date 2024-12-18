import warnings
warnings.filterwarnings("ignore")
from langchain_google_genai import ChatGoogleGenerativeAI
import os 
from typing import Dict
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from langchain_groq import ChatGroq
import sqlite3
from helper_agents import *
from pydantic_classes import *
from database_management import DatabaseManager
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from pathlib import Path


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ['GOOGLE_API_KEY'] = os.getenv("GEMINI_API_KEY")

llm= ChatGoogleGenerativeAI(model=os.getenv("GEMINI_FLASH"))
# llm = ChatGroq(model = os.getenv("LLAMA_70B_GROQ"))

    
def extract_email_intent(state: AgentState):
    print("> Email Classification")
    parser = JsonOutputParser(pydantic_object=intent)
    with open(Path("prompt_templates\intent_classification.txt"), "r") as f:
        prompt_body = f.read()
    
    prompt = PromptTemplate(template=prompt_body, 
                            input_variables=["email"], 
                            partial_variables={"format_instructions":parser.get_format_instructions()},)

    chain = prompt | llm | parser

    result = chain.invoke({"email": state.input_email})
    state.intent = result.get("intent")
    print(state, "\n\n")
    
    return state

def extract_event_entities(state: AgentState):
    print("> Email Entity Extraction")
    parser = JsonOutputParser(pydantic_object=email_entity)
    with open(Path("prompt_templates\entity_extraction.txt"), "r") as f:
        prompt_body = f.read()
    prompt = PromptTemplate(template=prompt_body, input_variables=["email"], 
                                 partial_variables={"format_instructions":parser.get_format_instructions()},)

    chain = prompt | llm | parser

    result = chain.invoke({"email": state.input_email})
    print(result, "\n\n")
    state.order_id = result.get("order_id")
    state.customer_email = result.get("customer_email")
    state.product_name = result.get("product_name")
    # state.complaint_details = result.get("complaint_details")
    return state


def process_feedback(state: AgentState):
    print("> Feedback Processing")
    res = DatabaseManager.fetch_order(state.order_id)
    if not res:
        state.response = "Invalid Order. Cannot Process Feedback"
        return state
    if res['status'] != "D":
        state.response = "Order not yet delivered. Feeback can only be given after delivery"
        return state
    
    # create a simple chain to get the sentiment of the email
    state.sentiment = analyse_sentiment(state.input_email)
    DatabaseManager.insert_feedback(state)
    state.response = "Successfully Registered Feedback"

    return state

def process_complaint_followup(state: AgentState):
    print("> Followup Complaint")
    res = DatabaseManager.fetch_complaint(order_id=state.order_id)
    state.response = f"complaint_id: {res.complaint_id}\n status: {res.status}"

    return state

def process_new_complaint(state: AgentState):
    print("> New Complaint")
    res = DatabaseManager.fetch_order(order_id = state.order_id)
    print(res)
    if not res:
        state.response = f"No Orders Found with order_id = {state.order_id}"
        return state
    if res['status'] == "R":
        state.response = "This order has been returned by the customer. They are no longer allowed to register a complaint"
        return state
    if res["status"] == "T":
        state.response = "This order is in transit and not yet delivered. Complaint can only be registered after delivery"
        return state

    res = DatabaseManager.fetch_complaint(order_id = state.order_id)
    
    if res:
        state.response = "Open Complaint already exists for this order. New complaint can only be registered after active complaints are closed"
    
    else:
        # create a chain for getting complaint summary and product details
        summary = get_complaint_summary(email_body=state.input_email)
        state.complaint_summary = summary
        res =  DatabaseManager.insert_complaint(state)
        state.response = f"Complaint successfully registered.\nComplaint_id: {res}"
    return state

def process_product_recommendation(state: AgentState):
    print("> Product Recommendation")
    # criteria_prompt = ChatPromptTemplate.from_template("""
    # Extract product recommendation criteria from email:
    # {email}
    # """)
    #
    # criteria_chain = criteria_prompt | llm | StrOutputParser()
    # criteria = criteria_chain.invoke({"email":state.input_email})
    state.products = get_recommended_products(query=state.input_email)

    prompt = ChatPromptTemplate.from_template("""
    Draft a personalized product recommendation email.
    Customer Email: {customer_email}
    Recommended Products: {products}
    """)

    chain = prompt | llm | StrOutputParser()
    state.response = chain.invoke({
        "customer_email": state.input_email,
        "products": state.products
    })

    return state

def process_incomplete_info(state: AgentState):
    print("> Incomplete Input Email")

    state = extract_email_intent(state=state)
    if state.intent.strip() == "Product Recommendation":
        print("product recommendation email detected")
        state = process_product_recommendation(state)
        return state

    parser= JsonOutputParser(pydantic_object=response_email)
    with open(Path("prompt_templates\incomplete_content_response.txt"), "r") as f:
        prompt_body = f.read()
    
    prompt = PromptTemplate(template=prompt_body, input_variables=["email"],
                            partial_variables={"format_instructions":parser.get_format_instructions()},)
    chain = prompt | llm | StrOutputParser()
    state.response = chain.invoke({"email": state.input_email})
    print(state.response, "\n\n")

    return state


def format_response(state: AgentState):
    print("> Formatting Final Response")
    parser = JsonOutputParser(pydantic_object=response_email)
    with open(Path(r"prompt_templates\format_email_response.txt"), "r") as f:
        prompt_body = f.read()
    
    prompt = PromptTemplate(template=prompt_body,
                            input_variables=["upstream_response", "intent"], 
                            partial_variables={"format_instructions":parser.get_format_instructions()},)
    chain = prompt | llm | parser

    result = chain.invoke({"upstream_response": state.response, "intent": state.intent})
    state.response = result.get("response_email_body")
    return state

def helper_conditional_edge_1(state: AgentState):
    if not state.order_id:
        return "incomplete_data"
    return "process_further"