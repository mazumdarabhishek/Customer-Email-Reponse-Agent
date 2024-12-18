import warnings
warnings.filterwarnings("ignore")

import os 
from typing import Dict
from dotenv import load_dotenv
load_dotenv()
from helper_agents import *
from pydantic_classes import *
from langgraph.graph import StateGraph, END, START

os.environ['LANGCHAIN_TRACING_V2'] = "true"
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

from email_processes import *


def build_graph():
    
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("extract_entities", extract_event_entities)
    graph_builder.add_node("extract_intent", extract_email_intent)
    graph_builder.add_node("process_feedback", process_feedback)
    graph_builder.add_node("complaint_followup", process_complaint_followup)
    graph_builder.add_node("new_complaint", process_new_complaint)
    # graph_builder.add_node("product_recommendation", process_product_recommendation)
    graph_builder.add_node("incomplete_email", process_incomplete_info)
    graph_builder.add_node("format_response", format_response)

    # CONDITIONAL EDGE FOR INCOMPLETE CUSTOMER EMAIL
    graph_builder.add_conditional_edges(
        "extract_entities",
        helper_conditional_edge_1,
        {
            "incomplete_data": "incomplete_email",
            "process_further": "extract_intent"
        }
    )

    # CONDITIONAL EDGE FOR DIFFERENT EMAIL CATEGORIES
    graph_builder.add_conditional_edges(
        "extract_intent",
        lambda state: state.intent,
        {
            "Feedback": "process_feedback",
            "Complaint Followup": "complaint_followup",
            "New Complaint": "new_complaint",
            # "Product Recommendation": "product_recommendation"
        }
    )

    graph_builder.add_edge(START, "extract_entities")

    graph_builder.add_edge("incomplete_email", END)

    graph_builder.add_edge("process_feedback", "format_response")

    graph_builder.add_edge("complaint_followup", "format_response")

    graph_builder.add_edge("new_complaint", "format_response")

    # graph_builder.add_edge("product_recommendation", "format_response")

    graph_builder.add_edge("format_response", END)

    return graph_builder.compile()

    
def main():
    agent = build_graph()

    # COMPLAINT EMAIL PROCESS
    # sample_email = """
    # I am writing about a complaint regarding a skincare product I purchased from sephora website on 24th November.
    # The product cause rashes and skin irritation in my face and I had to visit the doctor for the same.
    # I want to return and have a refund for the product.
    # Below are the product details:
    # order_id: 8
    # email: alice.johnson@example.com
    # product_name: ABC lotion
    # """

    # FEEDBACK EMAIL PROCESS
    # sample_email = """
    # I received my order in good condition and The product is worth every penny. I am really noticing results on my skin. Great Product. Must recommended
    # Below are the product details:
    # order_id: 8
    # email: alice.johnson@example.com
    # product_name: ABC lotion
    # """

    sample_email = """
      show me products with rating higher that 4.5"""

    state = AgentState(input_email = sample_email)

    response = agent.invoke(state)
    print("="*10 + "RESPONSE EMAIL"+"="*10, f"\n\n {response.get('response')}")


if __name__ == "__main__":

    main()