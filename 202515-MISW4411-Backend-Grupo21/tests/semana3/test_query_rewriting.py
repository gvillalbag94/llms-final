"""
Tests para verificar la funcionalidad de query rewriting en Semana 3.

Este test verifica que cuando use_query_rewriting=True:
1. El final_query es diferente de la question original
2. El query_rewriting_used es True
3. El endpoint responde correctamente
"""

import pytest
import httpx
import asyncio
import time
from typing import Dict, Any


class TestQueryRewriting:
    """Pruebas para verificar que el query rewriting funciona correctamente."""
    
    BASE_URL = "http://localhost:8000"
    TEST_QUESTION = "¿Qué información importante contienen estos documentos?"
    
    @pytest.fixture(scope="class")
    def base_url(self) -> str:
        """URL base del servidor para las pruebas."""
        return self.BASE_URL
    
    @pytest.fixture(scope="class")
    def test_question(self) -> str:
        """Pregunta de prueba que debe ser reescrita."""
        return self.TEST_QUESTION
    
    def test_ask_endpoint_with_query_rewriting_exists(self, base_url: str):
        """
        Test básico: Verificar que el endpoint /ask existe y responde con query rewriting.
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/api/v1/ask",
                json={
                    "question": self.TEST_QUESTION,
                    "top_k": 5,
                    "collection": "test_collection",
                    "use_query_rewriting": True
                },
                timeout=180.0
            )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            data = response.json()
            assert "question" in data, "Response should contain 'question' field"
            assert "final_query" in data, "Response should contain 'final_query' field"
            assert "query_rewriting_used" in data, "Response should contain 'query_rewriting_used' field"
            assert "answer" in data, "Response should contain 'answer' field"
    
    def test_query_rewriting_functionality(self, base_url: str, test_question: str):
        """
        Test principal: Verificar que el query rewriting funciona correctamente.
        
        Verifica:
        1. query_rewriting_used = True cuando use_query_rewriting=True
        2. final_query es diferente de la question original
        3. final_query no es vacío o null
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/api/v1/ask",
                json={
                    "question": test_question,
                    "top_k": 5,
                    "collection": "test_collection",
                    "use_query_rewriting": True
                },
                timeout=180.0
            )
            
            assert response.status_code == 200, f"Request failed: {response.status_code} - {response.text}"
            
            data = response.json()
            
            # 1. Verificar que el query rewriting se utilizó
            assert data.get("query_rewriting_used") is True, "query_rewriting_used should be True when use_query_rewriting=True"
            
            # 2. Verificar que final_query existe y no es vacío
            final_query = data.get("final_query")
            assert final_query is not None, "final_query should not be null"
            assert final_query.strip() != "", "final_query should not be empty"
            
            # 3. Verificar que final_query es diferente de la question original
            original_question = data.get("question")
            assert final_query != original_question, (
                f"final_query should be different from original question when query rewriting is enabled. "
                f"Original: '{original_question}', Final: '{final_query}'"
            )
            
            # 4. Verificar que final_query tiene contenido sustancial (no solo cambios menores)
            # Permitimos cierta flexibilidad, pero debe haber una diferencia real
            original_words = set(original_question.lower().split())
            final_words = set(final_query.lower().split())
            
            # Debe haber al menos una palabra nueva o diferente estructura
            words_added = final_words - original_words
            assert len(words_added) > 0 or len(final_query) > len(original_question) * 1.1, (
                f"Query rewriting should add meaningful content or restructure the query. "
                f"Original: '{original_question}', Final: '{final_query}'"
            )
            
            print(f"✅ Query rewriting test passed:")
            print(f"   Original: '{original_question}'")
            print(f"   Rewritten: '{final_query}'")
            print(f"   Words added: {words_added}")
    
    def test_query_rewriting_disabled_functionality(self, base_url: str, test_question: str):
        """
        Test de control: Verificar el comportamiento cuando query rewriting está deshabilitado.
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/api/v1/ask",
                json={
                    "question": test_question,
                    "top_k": 5,
                    "collection": "test_collection",
                    "use_query_rewriting": False  # Query rewriting deshabilitado
                },
                timeout=180.0
            )
            
            assert response.status_code == 200, f"Request failed: {response.status_code} - {response.text}"
            
            data = response.json()
            
            # Cuando query rewriting está deshabilitado
            assert data.get("query_rewriting_used") is False, "query_rewriting_used should be False when use_query_rewriting=False"
            
            # final_query debe ser igual a la question original
            final_query = data.get("final_query")
            original_question = data.get("question")
            
            assert final_query == original_question, (
                f"final_query should equal original question when query rewriting is disabled. "
                f"Original: '{original_question}', Final: '{final_query}'"
            )
            
            print(f"✅ Query rewriting disabled test passed - final_query equals original question")
    
    def test_query_rewriting_preserves_meaning(self, base_url: str, test_question: str):
        """
        Test adicional: Verificar que el query rewriting preserva el significado básico.
        
        Esto es un test más sofisticado que verifica que la consulta reescrita
        mantiene palabras clave importantes de la consulta original.
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/api/v1/ask",
                json={
                    "question": test_question,
                    "top_k": 5,
                    "collection": "test_collection",
                    "use_query_rewriting": True
                },
                timeout=180.0
            )
            
            assert response.status_code == 200, f"Request failed: {response.status_code} - {response.text}"
            
            data = response.json()
            final_query = data.get("final_query", "").lower()
            
            # Verificar que la consulta reescrita mantiene conceptos clave
            # Para nuestra question test, debería mantener conceptos como "información", "documentos", etc.
            key_concepts = ["información", "informacion", "document", "content", "datos", "importante"]
            
            has_key_concept = any(concept in final_query for concept in key_concepts)
            assert has_key_concept, (
                f"Rewritten query should preserve key concepts from original question. "
                f"Final query: '{final_query}' should contain one of: {key_concepts}"
            )
            
            print(f"✅ Meaning preservation test passed - key concepts maintained in rewritten query")
    
    def test_both_features_combined(self, base_url: str, test_question: str):
        """
        Test combinado: Verificar que reranking y query rewriting funcionan juntos.
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/api/v1/ask",
                json={
                    "question": test_question,
                    "top_k": 5,
                    "collection": "test_collection",
                    "use_reranking": True,
                    "use_query_rewriting": True
                },
                timeout=180.0
            )
            
            assert response.status_code == 200, f"Request failed: {response.status_code} - {response.text}"
            
            data = response.json()
            
            # Verificar que ambas funcionalidades están activas
            assert data.get("reranker_used") is True, "reranker_used should be True"
            assert data.get("query_rewriting_used") is True, "query_rewriting_used should be True"
            
            # Verificar query rewriting
            final_query = data.get("final_query")
            original_question = data.get("question")
            assert final_query != original_question, "final_query should be different from original"
            
            # Verificar reranking
            context_docs = data.get("context_docs", [])
            if len(context_docs) > 0:
                for doc in context_docs:
                    assert doc.get("rerank_score") is not None, "rerank_score should not be null"
            
            print(f"✅ Combined features test passed - both reranking and query rewriting working together")


if __name__ == "__main__":
    # Permitir ejecutar el test directamente
    pytest.main([__file__, "-v"])
