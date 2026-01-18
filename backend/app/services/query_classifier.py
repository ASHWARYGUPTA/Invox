"""
Query Classifier using Google Gemini
Classifies user queries into ANALYTICAL or SEMANTIC
"""

from google import genai
from google.genai import types
from typing import Literal
from app.core.config import settings

QueryType = Literal['ANALYTICAL', 'SEMANTIC']


class QueryClassifier:
    """Classifies user queries into ANALYTICAL or SEMANTIC"""
    
    CLASSIFICATION_PROMPT = """
You are a query classifier for an invoice management system.

Classify the following user query into ONE of these types:

1. ANALYTICAL - Requires SQL/aggregation/filtering/listing:
   - List queries: "list all", "show all", "get all", "show me"
   - Questions with: sum, total, average, count, most, least, top, bottom
   - Comparisons: more than, less than, between, greater than, under, over
   - Time-based: monthly, weekly, last month, this year, in 2024
   - Aggregations: group by vendor, by date, by status
   - Filtering: pending invoices, paid invoices, overdue invoices
   - Statistics: how many, what is the total, average amount
   - IMPORTANT: "list all invoices" is ANALYTICAL

2. SEMANTIC - Requires similarity/context/semantic search:
   - Context-based: "invoices from Acme Corp", "office supplies purchases"
   - Similar to: "like this", "similar invoices"
   - Vague/fuzzy: "tell me about", "search for", "find things related to"
   - Natural language: "show me invoices related to technology"
   - When user doesn't specify exact criteria but describes concept

User Query: {query}

Think step by step:
- Does the query ask for ALL items or need SQL listing? → ANALYTICAL
- Does the query need aggregation (sum, count, average)? → ANALYTICAL  
- Does the query need semantic similarity search? → SEMANTIC

Respond with ONLY one word: ANALYTICAL or SEMANTIC
"""
    
    def __init__(self):
        """Initialize Gemini model"""
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.0-flash-exp'
    
    def classify(self, query: str) -> QueryType:
        """
        Classify query type
        Returns: 'ANALYTICAL' or 'SEMANTIC'
        """
        # Rule-based pre-check for obvious analytical queries
        query_lower = query.lower()
        analytical_keywords = [
            'list all', 'show all', 'get all', 'all invoices',
            'sum', 'total', 'average', 'count', 'how many',
            'most', 'least', 'top', 'bottom',
            'more than', 'less than', 'between', 'greater than',
            'monthly', 'weekly', 'last month', 'this year',
            'group by', 'aggregate', 'pending', 'paid', 'overdue'
        ]
        
        # Check for obvious analytical patterns
        for keyword in analytical_keywords:
            if keyword in query_lower:
                print(f"🎯 Quick match: '{keyword}' found → ANALYTICAL")
                return 'ANALYTICAL'
        
        # Otherwise, use Gemini classification
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=self.CLASSIFICATION_PROMPT.format(query=query),
                config=types.GenerateContentConfig(
                    temperature=0,
                    max_output_tokens=10
                )
            )
            
            raw_response = response.text.strip().upper()
            classification = raw_response
            
            print(f"🔍 Query: '{query}'")
            print(f"📊 Gemini raw response: '{raw_response}'")
            print(f"✅ Classification: {classification}")
            
            # Fallback to ANALYTICAL if unclear
            if classification not in ['ANALYTICAL', 'SEMANTIC']:
                print(f"⚠️  Invalid classification '{classification}', defaulting to ANALYTICAL")
                classification = 'ANALYTICAL'
            
            return classification
            
        except Exception as e:
            print(f"Error in query classifier: {e}")
            print(f"Defaulting to ANALYTICAL query type")
            return 'ANALYTICAL'  # Safe fallback
