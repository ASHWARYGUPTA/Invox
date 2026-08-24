"""
Hybrid Query Engine
Orchestrates SQL Agent and RAG System with OpenRouter for response synthesis
"""

from .query_classifier import QueryClassifier
from .sql_agent import SQLAgent
from .rag_system import RAGSystem
from openai import OpenAI
from typing import Dict, Any
import json
from sqlalchemy.orm import Session
from app.core.config import settings


class HybridQueryEngine:
    """Orchestrates SQL Agent and RAG System"""
    
    def __init__(self):
        self.classifier = QueryClassifier()
        self.sql_agent = SQLAgent()
        self.rag_system = RAGSystem()
        
        # Initialize OpenRouter for response synthesis
        api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model_name = getattr(settings, 'LLM_MODEL', None) or getattr(settings, 'OPENROUTER_MODEL_NAME', 'google/gemma-4-26b-a4b-it:free')
    
    def query(self, user_query: str, user_id: str, db: Session) -> Dict[str, Any]:
        """
        Main entry point for all queries
        Routes to appropriate system and synthesizes response
        """
        try:
            # Step 1: Classify query
            query_type = self.classifier.classify(user_query)
            
            print(f"Query classified as: {query_type}")
            
            # Step 2: Execute appropriate system
            if query_type == 'ANALYTICAL':
                results = self.sql_agent.query(user_query, user_id, db)
                context_type = 'sql'
            else:
                results = self.rag_system.search(user_query, user_id)
                context_type = 'semantic'
            
            # Step 3: Synthesize response
            response = self._synthesize_response(
                user_query=user_query,
                results=results,
                context_type=context_type
            )
            
            return {
                'success': True,
                'query': user_query,
                'query_type': query_type,
                'raw_results': results,
                'response': response
            }
        
        except Exception as e:
            print(f"Error in hybrid query engine: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': user_query,
                'response': f"I encountered an error processing your query: {str(e)}"
            }
    
    def _synthesize_response(self, 
                            user_query: str, 
                            results: Dict, 
                            context_type: str) -> str:
        """Generate natural language response from results using OpenRouter"""
        
        synthesis_prompt = f"""
You are a helpful financial assistant explaining invoice query results to a user.

User asked: "{user_query}"

Query type: {context_type}

Results:
{json.dumps(results, indent=2, default=str)}

Generate a clear, concise answer:
1. Directly answer the question in natural language
2. Include key numbers/facts from the results
3. If the results are empty, say "I couldn't find any invoices matching your query."
4. If there are multiple results, summarize them clearly
5. Keep it conversational and helpful
6. Format numbers nicely (e.g., $1,234.56)
7. If showing a list, keep it organized and easy to read

Answer:
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": synthesis_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            message = response.choices[0].message
            content = message.content or getattr(message, 'reasoning', None) or ""
            if not content.strip():
                raise ValueError("Empty content and reasoning in LLM response")
            return content.strip()
        
        except Exception as e:
            print(f"Error synthesizing response: {e}")
            # Fallback to simple response
            if context_type == 'sql' and results.get('success'):
                row_count = results.get('row_count', 0)
                if row_count == 0:
                    return "I couldn't find any invoices matching your query."
                else:
                    return f"I found {row_count} invoice(s) matching your query. Here are the results: {json.dumps(results.get('results', []), indent=2)}"
            else:
                return f"Error generating response: {str(e)}"
