"""
Chat API Endpoints for Invoice RAG System
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.services.hybrid_query_engine import HybridQueryEngine
from app.services.rag_system import RAGSystem

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model"""
    query: str


class ChatResponse(BaseModel):
    """Chat response model"""
    success: bool
    query: str
    query_type: Optional[str] = None
    response: str
    raw_results: Optional[Dict] = None
    error: Optional[str] = None


class IndexRequest(BaseModel):
    """Index request model"""
    force_reindex: bool = False


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a chat query about invoices
    
    Routes query to either:
    - SQL Agent (for analytical queries)
    - RAG System (for semantic search)
    
    Returns natural language response
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Initialize hybrid query engine
        engine = HybridQueryEngine()
        
        # Process query
        result = engine.query(
            user_query=request.query,
            user_id=str(current_user.id),
            db=db
        )
        
        return ChatResponse(
            success=result.get('success', True),
            query=result.get('query'),
            query_type=result.get('query_type'),
            response=result.get('response'),
            raw_results=result.get('raw_results'),
            error=result.get('error')
        )
    
    except Exception as e:
        print(f"Error in chat query: {e}")
        return ChatResponse(
            success=False,
            query=request.query,
            response=f"I encountered an error: {str(e)}",
            error=str(e)
        )


@router.post("/index")
async def index_invoices(
    request: IndexRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Index all invoices for the current user
    
    This enables semantic search over invoices.
    Run this after uploading new invoices or when setting up chat for the first time.
    """
    try:
        rag_system = RAGSystem()
        
        # Run indexing in background
        background_tasks.add_task(
            rag_system.bulk_index_invoices,
            db=db,
            user_id=str(current_user.id)
        )
        
        return {
            "success": True,
            "message": "Indexing started in background. This may take a few moments."
        }
    
    except Exception as e:
        print(f"Error starting invoice indexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def chat_status(
    current_user: User = Depends(deps.get_current_user)
):
    """
    Check if chat system is ready
    """
    try:
        # Check if services are initialized
        rag_system = RAGSystem()
        
        return {
            "success": True,
            "ready": True,
            "message": "Chat system is ready"
        }
    
    except Exception as e:
        return {
            "success": False,
            "ready": False,
            "error": str(e)
        }
