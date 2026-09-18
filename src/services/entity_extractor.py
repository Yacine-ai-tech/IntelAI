"""
Entity Extraction Service for GraphRAG-lite

Extracts entities from KPI records during ingestion to enable graph-based retrieval.
Entities: department, category, period, metric_name, etc.
"""

from typing import Dict, List, Optional, Any
import re


class EntityExtractor:
    """Extracts entities from KPI records for graph-based retrieval."""
    
    def __init__(self):
        # Common entity patterns
        self.department_patterns = {
            'finance': [
                'finance', 'financial', 'revenue', 'cost', 'profit', 'margin', 'cash', 'debt',
                'chiffre d affaires', 'chiffre d\'affaires', 'tresorerie', 'trésorerie',
                'benefice', 'bénéfice', 'dette', 'charges', 'resultat net', 'résultat net',
                'ebitda', 'amortissement', 'comptabilite', 'comptabilité', 'tresor', 'depenses',
                'dépenses', 'impots', 'impôts', 'financier', 'financière'
            ],
            'people': [
                'hr', 'people', 'employee', 'headcount', 'personnel', 'talent', 'workforce',
                'ressources humaines', 'rh', 'effectif', 'effectifs', 'salaries', 'salariés',
                'recrutement', 'embauche', 'demission', 'démission', 'absenteisme', 'absentéisme',
                'formation', 'remuneration', 'rémunération', 'salaire', 'salaires'
            ],
            'operations': [
                'ops', 'operations', 'oee', 'defect', 'inventory', 'throughput', 'efficiency',
                'exploitation', 'rendement', 'cadence', 'defauts', 'défauts', 'qualite', 'qualité',
                'fabrication', 'production', 'panne', 'arret', 'sécurité', 'securite', 'usine'
            ],
            'logistics': [
                'logistics', 'delivery', 'fulfillment', 'fulfilment', 'warehouse', 'supplier', 'freight', 'shipping',
                'logistique', 'livraison', 'entrepot', 'entrepôt', 'fournisseur', 'stocks',
                'rupture de stock', 'fret', 'expedition', 'expédition', 'delai', 'délai', 'transport'
            ],
            'growth': [
                'growth', 'customer', 'mrr', 'arr', 'churn', 'acquisition', 'ltv', 'cac', 'sales',
                'croissance', 'vente', 'ventes', 'commercial', 'clients', 'attrition', 'revenu recurrent',
                'revenu récurrent', 'prospection'
            ],
            'it': [
                'uptime', 'latency', 'vulnerabilit', 'deployment', 'incident', 'security',
                'mttr', 'resolution', 'sla', 'devops', 'change failure',
                # French infrastructure / IT terms
                'ordinateur', 'serveur', 'informatique', 'achat', 'materiel',
                'infrastructure', 'financement', 'capex', 'logiciel', 'reseau',
                'cloud', 'systeme', 'equipement', 'departement it', 'departement informatique'
            ],
            'esg': [
                'emission', 'carbon', 'renewable', 'diversity', 'governance', 'sustainab',
                'waste', 'water consumption', 'audit compliance',
                # French ESG terms
                'rse', 'environnement', 'carbone', 'renouvelable', 'dechets', 'déchets',
                'diversite', 'diversité', 'gouvernance', 'durabilite', 'durabilité', 'eau'
            ],
        }
        # Characters that indicate a malformed / synthetic token — skip these as entities
        self._bad_entity_chars = re.compile(r'[()=<>%,;:"]')
        
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
        """Infer department from category and metric name.

        Two tiers, in order:
        1. Trust an already-known, clean `category` field directly. Structured KPI
           records are ingested with a real domain tag (category="IT", "ESG", etc.) —
           the old code ignored that and went straight to a keyword scan over
           metric_name, so an IT/ESG row whose metric name happened to contain none
           of that domain's keywords got no department at all (the measured 71.4%/
           91.7% coverage ceiling on IT/ESG vs 100% on the other 5 domains, whose
           metric vocabulary is more keyword-distinctive — see BENCHMARK.md §2a).
        2. Fall back to a weighted multi-pattern vote across ALL domains — not the
           previous first-match scan, which always resolved shared vocabulary (e.g.
           "audit compliance" appearing in both ESG and Finance/Operations word
           lists) to whichever domain happened to be checked first in dict order.
           Voting by total matched-term count picks the domain with the strongest
           textual evidence instead.
        """
        category_lower = category.strip().lower() if category else ''
        metric_lower = metric_name.lower() if metric_name else ''

        if category_lower in self.department_patterns:
            return category_lower.capitalize()

        text = f'{category_lower} {metric_lower}'
        scores: Dict[str, int] = {}
        for dept, patterns in self.department_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            if score:
                scores[dept] = score
        if scores:
            return max(scores, key=scores.get).capitalize()

        return None
    
    def _extract_metric_subentities(self, metric_name: str) -> List[Dict[str, str]]:
        """Extract sub-entities from metric name (e.g., 'Revenue_US' -> Revenue, US)."""
        entities = []
        
        # Split on common separators
        parts = re.split(r'[_\s-]', metric_name)
        
        for part in parts:
            if len(part) > 2 and part not in entities:
                # Skip common words and tokens containing special characters that indicate
                # a synthetic / malformed value (e.g. '(moyenne(target', '=value>')
                if (part.lower() not in ['total', 'net', 'gross', 'avg']
                        and not self._bad_entity_chars.search(part)):
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