import os
from dotenv import load_dotenv
from google import genai

# Load .env
load_dotenv()

# Create Gemini client
import streamlit as st

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key)


def generate_ai_insight(question, summary):
    
    prompt = f"""
You are a Senior Business Strategy Consultant.

You are analyzing a company's sales dashboard.

Business Data:

{summary}

User Question:
{question}

Your response MUST follow this exact format.

# 📋 Executive Summary
(2-3 sentences)

# 📊 Key Findings
- Finding 1
- Finding 2
- Finding 3

# ⚠ Business Risks
- Risk 1
- Risk 2

# 🚀 Growth Opportunities
- Opportunity 1
- Opportunity 2
- Opportunity 3

# ✅ Action Plan
1.
2.
3.

Rules:
- Maximum 250 words.
- Be professional.
- Use bullet points.
- Use markdown.
- Focus on business decisions.
- Never repeat the dataset.
"""