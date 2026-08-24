"""
Query Classifier using OpenRouter
Classifies user queries into ANALYTICAL or SEMANTIC
"""

from openai import OpenAI
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
        """Initialize OpenRouter model"""
        api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model_name = getattr(settings, 'LLM_MODEL', None) or getattr(settings, 'OPENROUTER_MODEL_NAME', 'google/gemma-4-26b-a4b-it:free')
    
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
        
        # Otherwise, use OpenRouter classification
        try:
            prompt = self.CLASSIFICATION_PROMPT.format(query=query)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=10
            )
            
            message = response.choices[0].message
            raw_content = message.content or getattr(message, 'reasoning', None) or ""
            raw_response = raw_content.strip().upper()
            classification = raw_response
            
            print(f"🔍 Query: '{query}'")
            print(f"📊 OpenRouter raw response: '{raw_response}'")
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
