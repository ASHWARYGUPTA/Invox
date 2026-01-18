"""
SQL Agent using Google Gemini
Generates and executes SQL queries for analytical questions
"""

from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List
import json
from app.core.config import settings


class SQLAgent:
    """Generates SQL queries for analytical questions about invoices"""
    
    SQL_GENERATION_PROMPT = """
You are a SQL expert for an invoice management system.

Database Schema:
- Table: invoices
  Columns:
  - id (UUID, Primary Key)
  - user_id (UUID, Foreign Key)
  - invoice_id (VARCHAR, invoice number)
  - vendor_name (VARCHAR)
  - customer_name (VARCHAR)
  - amount_due (FLOAT)
  - tax_amount (FLOAT)
  - subtotal (FLOAT)
  - currency (VARCHAR, default 'USD')
  - invoice_date (VARCHAR, format: YYYY-MM-DD)
  - due_date (VARCHAR, format: YYYY-MM-DD)
  - status (VARCHAR: 'pending', 'completed', 'failed', 'verified', 'paid', 'archived')
  - items (JSON, array of items)
  - vendor_address (VARCHAR)
  - customer_address (VARCHAR)
  - original_filename (VARCHAR)
  - created_at (TIMESTAMP)
  - updated_at (TIMESTAMP)

User Query: {query}
User ID: {user_id}

Generate a SQL query to answer this question. Requirements:
1. ALWAYS include WHERE user_id = '{user_id}' to filter by user
2. Use proper PostgreSQL syntax
3. Return only the SQL query, no explanations
4. For date comparisons, use string comparison (e.g., invoice_date >= '2024-01-01')
5. For listing queries, limit to 50 results
6. Use appropriate aggregations (SUM, COUNT, AVG) when needed

SQL Query:
"""
    
    def __init__(self):
        """Initialize Gemini model"""
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.0-flash-exp'
    
    def query(self, user_query: str, user_id: str, db: Session) -> Dict[str, Any]:
        """
        Generate SQL query and execute it
        Returns results as dict
        """
        try:
            # Generate SQL query
            sql_query = self._generate_sql(user_query, user_id)
            
            print(f"📊 Generated SQL: {sql_query}")
            
            # Execute query
            results = self._execute_query(sql_query, db)
            
            return {
                'success': True,
                'sql_query': sql_query,
                'results': results,
                'row_count': len(results)
            }
            
        except Exception as e:
            print(f"Error in SQL agent: {e}")
            return {
                'success': False,
                'error': str(e),
                'sql_query': None,
                'results': []
            }
    
    def _generate_sql(self, user_query: str, user_id: str) -> str:
        """Generate SQL query using Gemini"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=self.SQL_GENERATION_PROMPT.format(
                query=user_query,
                user_id=user_id
            ),
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=500
            )
        )
        
        sql_query = response.text.strip()
        
        # Clean up SQL query (remove markdown code blocks if present)
        if sql_query.startswith('```sql'):
            sql_query = sql_query[6:]
        if sql_query.startswith('```'):
            sql_query = sql_query[3:]
        if sql_query.endswith('```'):
            sql_query = sql_query[:-3]
        
        sql_query = sql_query.strip()
        
        # Ensure user_id filter is present
        if f"user_id = '{user_id}'" not in sql_query and f'user_id = "{user_id}"' not in sql_query:
            print(f"⚠️  Warning: user_id filter not found in generated SQL")
        
        return sql_query
    
    def _execute_query(self, sql_query: str, db: Session) -> List[Dict]:
        """Execute SQL query and return results as list of dicts"""
        result = db.execute(text(sql_query))
        
        # Convert to list of dicts
        columns = result.keys()
        rows = result.fetchall()
        
        results = []
        for row in rows:
            row_dict = {}
            for i, column in enumerate(columns):
                value = row[i]
                # Convert to JSON-serializable types
                if hasattr(value, 'isoformat'):  # datetime
                    value = value.isoformat()
                elif isinstance(value, bytes):
                    value = value.decode('utf-8')
                row_dict[column] = value
            results.append(row_dict)
        
        return results
