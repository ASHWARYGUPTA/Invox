"""
RAG System for Invoice Semantic Search
Uses ChromaDB and Google Gemini for embeddings and search
"""

import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
import json
import os
from sqlalchemy.orm import Session
from app.models.invoice import Invoice


class RAGSystem:
    """Semantic search over invoice descriptions"""
    
    def __init__(self, collection_name: str = "invoices"):
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Use lightweight embedding function (smaller model)
        # all-MiniLM-L6-v2 is only ~80MB vs larger models (>400MB)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
    
    def add_invoice(self, invoice: Dict[str, Any]):
        """Add an invoice to vector store"""
        # Create searchable text from invoice
        searchable_text = self._create_searchable_text(invoice)
        
        # Add to ChromaDB with user_id in metadata for filtering
        self.collection.add(
            documents=[searchable_text],
            metadatas=[{
                'invoice_id': str(invoice['id']),
                'user_id': str(invoice['user_id']),
                'vendor_name': str(invoice.get('vendor_name') or ''),
                'amount_due': str(invoice.get('amount_due', 0)),
                'invoice_date': str(invoice.get('invoice_date', '')),
                'status': str(invoice.get('status', 'pending'))
            }],
            ids=[f"inv_{invoice['id']}"]
        )
        print(f"✅ Added invoice {invoice['id']} to ChromaDB")
    
    def _create_searchable_text(self, invoice: Dict[str, Any]) -> str:
        """Create rich text representation for embedding"""
        # Include extracted text if available (contains full OCR content)
        extracted = invoice.get('extracted_text', '')
        
        # Build structured text
        text = f"""
        Invoice Number: {invoice.get('invoice_id', 'Unknown')}
        Date: {invoice.get('invoice_date', 'Unknown')}
        Due Date: {invoice.get('due_date', 'Unknown')}
        Vendor: {invoice.get('vendor_name', 'Unknown')}
        Amount: {invoice.get('amount_due', 0)} {invoice.get('currency', 'USD')}
        Status: {invoice.get('status', 'pending')}
        Filename: {invoice.get('original_filename', 'Unknown')}
        Confidence: {invoice.get('confidence_score', 0)}
        Notes: {invoice.get('notes', '')}
        
        Extracted Content:
        {extracted}
        """
        return text.strip()
    
    def search(self, query: str, user_id: str, n_results: int = 5) -> List[Dict]:
        """Semantic search for invoices"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"user_id": str(user_id)}
            )
            return results
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    
    def search_with_filter(self, 
                          query: str, 
                          user_id: str,
                          status: str = None,
                          date_from: str = None,
                          n_results: int = 5) -> List[Dict]:
        """Semantic search with metadata filters"""
        where_clause = {"user_id": str(user_id)}
        
        if status:
            where_clause["status"] = status
        
        if date_from:
            where_clause["invoice_date"] = {"$gte": date_from}
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause
            )
            return results
        except Exception as e:
            print(f"Error in filtered search: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    
    def bulk_index_invoices(self, db: Session, user_id: str):
        """Index all invoices for a user"""
        invoices = db.query(Invoice).filter(Invoice.user_id == user_id).all()
        
        for invoice in invoices:
            # Build invoice dict with actual Invoice model fields
            invoice_dict = {
                'id': str(invoice.id),
                'user_id': str(invoice.user_id),
                'invoice_id': invoice.invoice_id or 'N/A',
                'vendor_name': invoice.vendor_name or 'Unknown',
                'amount_due': float(invoice.amount_due) if invoice.amount_due else 0.0,
                'currency': invoice.currency_code or 'USD',
                'invoice_date': invoice.invoice_date or 'N/A',
                'due_date': invoice.due_date or 'N/A',
                'status': str(invoice.status.value) if invoice.status else 'pending',
                'original_filename': invoice.original_filename,
                'extracted_text': invoice.extracted_text or '',
                'confidence_score': float(invoice.confidence_score) if invoice.confidence_score else 0.0,
                'created_at': invoice.created_at.isoformat() if invoice.created_at else '',
                'notes': invoice.notes or ''
            }
            try:
                self.add_invoice(invoice_dict)
            except Exception as e:
                print(f"Error indexing invoice {invoice.id}: {e}")
                continue
        
        print(f"✅ Indexed {len(invoices)} invoices for user {user_id}")
