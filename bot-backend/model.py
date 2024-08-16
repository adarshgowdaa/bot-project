from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class FAQResponse(BaseModel):
    question: str
    answer: str


class ChatMessage(BaseModel):
    username: str
    chat_id: str
    user_message: str
    bot_response: str


class FAQResponses(BaseModel):
    responses: List[FAQResponse]


faq_data = FAQResponses(
    responses=[
        FAQResponse(question="store hours", answer="Our store hours are from 9 AM to 9 PM."),
        FAQResponse(question="home delivery", answer="Yes, we offer home delivery for all our products."),
        FAQResponse(question="return product", answer="You can return a product within 30 days with the receipt."),
        FAQResponse(question="refund policy", answer="Refunds are processed within 7-10 business days."),
        FAQResponse(question="store locations", answer="We have stores globally. Please visit our website for details."),
        FAQResponse(question="track order", answer="You can track your order using the tracking number provided in your email."),
        FAQResponse(question="loyalty program", answer="Yes, our Amazon Prime program offers discounts and benefits."),
        FAQResponse(question="modify order", answer="Orders can be modified within 24 hours of placement."),
        FAQResponse(question="payment methods", answer="We accept all major credit cards, PayPal, and Amazon gift cards."),
        FAQResponse(question="warranty policy", answer="We offer a 1-year warranty on many of our products.")
    ]
)


def handle_query(query: str, username: str) -> str:
    lower_query = query.lower()
    
    if lower_query in ["hi", "hello", "hey"]:
        return f"Hello, {username}! How can I assist you today?"

    for faq in faq_data.responses:
        if faq.question in lower_query:
            return faq.answer

    return "I'm not sure how to help with that. Please ask something else or type 'logout' to end the session."


def get_current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")