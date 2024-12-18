from pydantic import BaseModel, Field
from typing import List
from langchain_core.documents import Document
# Defining a Agent State 

class AgentState(BaseModel):
    input_email: str
    intent: str = None 
    customer_email: str = None
    order_id: int = None
    complaint_summary: str = None
    product_name: str = None
    action: str = None
    feedback: str = None
    response: str = None
    products: list[Document] = None
    sentiment: str = None

class intent(BaseModel):
    intent: str = Field(..., description="Intent of the emal body")

class email_entity(BaseModel):
    order_id: int = Field(...,description="The order ID of the product")
    customer_email: str = Field(...,description="The email ID of the customer")
    product_name: str = Field(...,description="Name of the product that the user is complaining for")
    # complaint_details: str = Field(...,description="A summary of the customer complaint in the not more that 30 words.")

class sentiment(BaseModel):
    sentiment_type : str = Field(..., description="The overal sentiment of the email from one of the allowed types")

class complaint_summary(BaseModel):
    summary: str = Field(..., description="Summary of the complaint in less than 30 words")


class response_email(BaseModel):
    response_email_body: str = Field(..., description="The email body for responding customer email")
    