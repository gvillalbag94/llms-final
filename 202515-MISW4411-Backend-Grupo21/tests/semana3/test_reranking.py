"""
Tests para verificar la funcionalidad de reranking en Semana 3.

Este test verifica que cuando use_reranking=True:
1. Los context_docs están ordenados por rerank_score en orden descendente
2. Todos los rerank_score son diferentes de null
3. El endpoint responde correctamente
"""

import pytest
import httpx
import asyncio
import time
from typing import Dict, Any, List


class TestReranking:
    """Pruebas para verificar que el reranking funciona correctamente."""
    
    BASE_URL = "http://localhost:8000"
    TEST_QUESTION = "¿Qué información importante contienen estos documentos?"
    
    @pytest.fixture(scope="class")
    def base_url(self) -> str:
        """URL base del servidor para las pruebas."""
        return self.BASE_URL
    
    @pytest.fixture(scope="class") 
    def test_question(self) -> str:
        """Pregunta de prueba que debe funcionar en cualquier dominio."""
        return self.TEST_QUESTION
    
    def test_ask_endpoint_with_reranking_exists(self, base_url: str):
        """
        Test básico: Verificar que el endpoint /ask existe y responde.
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/api/v1/ask",
                json={
                    "question": self.TEST_QUESTION,
                    "top_k": 5,
                    "collection": "test_collection",
                    "use_reranking": True
                },
                timeout=180.0
            )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            data = response.json()
            assert "question" in data, "Response should contain 'question' field"
            assert "answer" in data, "Response should contain 'answer' field"
            assert "reranker_used" in data, "Response should contain 'reranker_used' field"
            assert "context_docs" in data, "Response should contain 'context_docs' field"
    
    def test_reranking_functionality(self, base_url: str, test_question: str):
        """
        Test principal: Verificar que el reranking funciona correctamente.
        
        Verifica:
        1. reranker_used = True cuando use_reranking=True
        2. Los context_docs tienen rerank_score no null
        3. Los documentos están ordenados por rerank_score descendente
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/api/v1/ask",
                json={
                    "question": test_question,
                    "top_k": 5,
                    "collection": "test_collection", 
                    "use_reranking": True
                },
                timeout=180.0
            )
            
            assert response.status_code == 200, f"Request failed: {response.status_code} - {response.text}"
            
            data = response.json()
            
            # 1. Verificar que el reranker se utilizó
            assert data.get("reranker_used") is True, "reranker_used should be True when use_reranking=True"
            
            # 2. Verificar que hay documentos de contexto
            context_docs = data.get("context_docs", [])
            assert len(context_docs) > 0, "Should have at least one context document when reranking is enabled"
            
            # 3. Verificar que todos los documentos tienen rerank_score no null
            for i, doc in enumerate(context_docs):
                assert "rerank_score" in doc, f"Document {i} should have rerank_score field"
                assert doc["rerank_score"] is not None, f"Document {i} rerank_score should not be null when reranking is used"
                assert isinstance(doc["rerank_score"], (int, float)), f"Document {i} rerank_score should be numeric"
            
            # 4. Verificar orden descendente por rerank_score
            if len(context_docs) > 1:
                rerank_scores = [doc["rerank_score"] for doc in context_docs]
                sorted_scores = sorted(rerank_scores, reverse=True)
                
                assert rerank_scores == sorted_scores, (
                    f"Documents should be ordered by rerank_score in descending order. "
                    f"Got scores: {rerank_scores}, expected: {sorted_scores}"
                )
            
            print(f"✅ Reranking test passed - {len(context_docs)} documents ordered correctly")
            print(f"   Rerank scores: {[doc['rerank_score'] for doc in context_docs]}")
    
    def test_reranking_disabled_functionality(self, base_url: str, test_question: str):
        """
        Test de control: Verificar el comportamiento cuando reranking está deshabilitado.
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/api/v1/ask",
                json={
                    "question": test_question,
                    "top_k": 5,
                    "collection": "test_collection",
                    "use_reranking": False  # Reranking deshabilitado
                },
                timeout=180.0
            )
            
            assert response.status_code == 200, f"Request failed: {response.status_code} - {response.text}"
            
            data = response.json()
            
            # Cuando reranking está deshabilitado
            assert data.get("reranker_used") is False, "reranker_used should be False when use_reranking=False"
            
            # Los documentos pueden o no tener rerank_score, pero si lo tienen debe ser null
            context_docs = data.get("context_docs", [])
            for i, doc in enumerate(context_docs):
                if "rerank_score" in doc:
                    assert doc["rerank_score"] is None, f"Document {i} rerank_score should be null when reranking is disabled"
            
            print(f"✅ Reranking disabled test passed - reranker_used=False, scores are null")
    
    def test_reranking_scores_are_different(self, base_url: str, test_question: str):
        """
        Test adicional: Verificar que los rerank_scores son diferentes entre documentos.
        
        Esto asegura que el reranking realmente está funcionando y no solo
        asignando el mismo score a todos los documentos.
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/api/v1/ask",
                json={
                    "question": test_question,
                    "top_k": 5,
                    "collection": "test_collection",
                    "use_reranking": True
                },
                timeout=180.0
            )
            
            assert response.status_code == 200, f"Request failed: {response.status_code} - {response.text}"
            
            data = response.json()
            context_docs = data.get("context_docs", [])
            
            if len(context_docs) > 1:
                rerank_scores = [doc["rerank_score"] for doc in context_docs]
                unique_scores = set(rerank_scores)
                
                # Verificar que hay al menos 2 scores diferentes (para evitar empates perfectos)
                # En casos reales, es muy improbable que todos los documentos tengan exactamente el mismo score
                assert len(unique_scores) >= 2 or len(context_docs) <= 2, (
                    f"Reranking should produce different scores for different documents. "
                    f"Got scores: {rerank_scores} (only {len(unique_scores)} unique values)"
                )
                
                print(f"✅ Score diversity test passed - {len(unique_scores)} unique scores out of {len(context_docs)} documents")


if __name__ == "__main__":
    # Permitir ejecutar el test directamente
    pytest.main([__file__, "-v"])
