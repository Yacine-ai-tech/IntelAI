"""
Entity Extraction Service for GraphRAG-lite

Extracts entities from KPI records during ingestion to enable graph-based retrieval.
Entities: department, category, period, metric_name, etc.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import re


class EntityExtractor:
    """Extracts entities from KPI records for graph-based retrieval."""
    
    def __init__(self):
        # Common entity patterns
        self.department_patterns = {
            'finance': ['finance', 'financial', 'revenue', 'cost', 'profit', 'margin'],
            'people': ['hr', 'people', 'employee', 'headcount', 'personnel'],
            'operations': ['ops', 'operations', 'logistics', 'inventory'],
            'growth': ['growth', 'customer', 'mrr', 'churn', 'acquisition'],
        }
        
        self.period_patterns = {
            'quarterly': r'Q[1-4]',
            'monthly': r'\d{4}-\d{2}',
            'yearly': r'\d{4}',
        }
    
    def extract_entities(self, kpi_record: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract entities from a KPI record.
        
        Args:
            kpi_record: Dictionary containing KPI data
            
        Returns:
            List of entity dictionaries with type and value
        """
        entities = []
        
        # Extract department/category
        category = kpi_record.get('category', '')
        metric_name = kpi_record.get('metric_name', kpi_record.get('name', ''))
        
        # Department entity
        dept = self._infer_department(category, metric_name)
        if dept:
            entities.append({
                'entity_type': 'department',
                'entity_value': dept,
                'confidence': 0.8,
            })
        
        # Category entity
        if category:
            entities.append({
                'entity_type': 'category',
                'entity_value': category,
                'confidence': 1.0,
            })
        
        # Period entity
        period = kpi_record.get('period', kpi_record.get('date', ''))
        if period:
            entities.append({
                'entity_type': 'period',
                'entity_value': period,
                'confidence': 1.0,
            })
        
        # Metric name entity
        if metric_name:
            # Extract sub-entities from metric name
            sub_entities = self._extract_metric_subentities(metric_name)
            entities.extend(sub_entities)
        
        return entities
    
    def _infer_department(self, category: str, metric_name: str) -> Optional[str]:
        """Infer department from category and metric name."""
        category_lower = category.lower() if category else ''
        metric_lower = metric_name.lower() if metric_name else ''
        
        for dept, patterns in self.department_patterns.items():
            for pattern in patterns:
                if pattern in category_lower or pattern in metric_lower:
                    return dept.capitalize()
        
        return None
    
    def _extract_metric_subentities(self, metric_name: str) -> List[Dict[str, str]]:
        """Extract sub-entities from metric name (e.g., 'Revenue_US' -> Revenue, US)."""
        entities = []
        
        # Split on common separators
        parts = re.split(r'[_\s-]', metric_name)
        
        for part in parts:
            if len(part) > 2 and part not in entities:
                # Skip common words
                if part.lower() not in ['total', 'net', 'gross', 'avg']:
                    entities.append({
                        'entity_type': 'metric_subentity',
                        'entity_value': part,
                        'confidence': 0.6,
                    })
        
        return entities
    
    def extract_query_entities(self, query: str) -> List[str]:
        """
        Extract entities from a query for graph-based retrieval.
        
        Args:
            query: User query string
            
        Returns:
            List of extracted entities
        """
        entities = []
        
        # Simple keyword-based extraction
        for dept, patterns in self.department_patterns.items():
            for pattern in patterns:
                if pattern.lower() in query.lower():
                    if dept.capitalize() not in entities:
                        entities.append(dept.capitalize())
        
        # Extract category names
        if 'finance' in query.lower():
            entities.append('Finance')
        if 'people' in query.lower() or 'hr' in query.lower():
            entities.append('People')
        if 'growth' in query.lower():
            entities.append('Growth')
        if 'operations' in query.lower() or 'ops' in query.lower():
            entities.append('Operations')
        
        return entities
    
    def find_entity_overlap(self, query_entities: List[str], kpi_entities: List[List[Dict]]) -> Dict[str, List[int]]:
        """
        Find overlap between query entities and KPI record entities.
        
        Args:
            query_entities: Entities extracted from query
            kpi_entities: List of entity lists for each KPI record
            
        Returns:
            Dictionary mapping KPI index to overlap score
        """
        overlap_scores = {}
        
        for i, record_entities in enumerate(kpi_entities):
            score = 0
            for q_ent in query_entities:
                for r_ent in record_entities:
                    if q_ent.lower() == r_ent.get('entity_value', '').lower():
                        score += r_ent.get('confidence', 0.5)
            if score > 0:
                overlap_scores[i] = score
        
        return overlap_scores


# Singleton instance
_entity_extractor = None

def get_entity_extractor() -> EntityExtractor:
    """Get the singleton entity extractor instance."""
    global _entity_extractor
    if _entity_extractor is None:
        _entity_extractor = EntityExtractor()
    return _entity_extractor