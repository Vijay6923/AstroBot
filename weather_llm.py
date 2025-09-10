import os
from pathlib import Path
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# ---------------- Config ---------------- #
INPUT_FILE = Path("data/weather_context.txt")

# Set your Groq API key
os.environ["GROQ_API_KEY"] = "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"

def load_weather_file(path):
    """Load weather context file"""
    if not path.exists():
        return "No weather data available. Please set a region first."
    
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def get_weather_response(question):
    """Get response for weather-related questions"""
    weather_data = load_weather_file(INPUT_FILE)
    
    template = """
You are a helpful weather assistant that answers based on the provided weather data.
Be concise but informative. If the data doesn't contain the answer, say so.

Weather Data:
{context}

Question: {question}

Provide a helpful and accurate answer:
"""
    
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=template
    )
    
    llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")
    chain = LLMChain(llm=llm, prompt=prompt)
    
    return chain.run({"context": weather_data, "question": question})