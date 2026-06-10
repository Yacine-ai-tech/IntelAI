"""
Internationalization (i18n) — Bilingual EN/FR support.

Every user-facing string goes through ``t(section, key)`` or
``I18N.get(section, key)``.  The chatbot, voice, and RAG systems also
use language-aware prompts so responses match the selected locale.

Usage::

    from src.core.i18n import t, I18N

    I18N.set_language("fr")
    print(t("AUTH", "login_button"))  # → "Se connecter"
"""
from __future__ import annotations

from typing import Dict, Literal

Language = Literal["en", "fr"]

class I18N:
    """Thread-safe i18n store for multilingual support."""

    _lang: Language = "en"

    # ── Auth ────────────────────────────────────────────────────────────
    AUTH: Dict[str, Dict[str, str]] = {
        "en": {
            "title": "IntelAI — Login",
            "username": "Username",
            "password": "Password",
            "login": "Login",
            "register": "Register",
            "signup_title": "Create Account",
            "role_label": "Select Role",
            "invalid": "Invalid username or password",
            "exists": "Username already exists",
            "created": "Account created successfully",
            "expired": "Session expired — please log in again.",
            "logout_ok": "Logged out successfully",
            "denied": "Access denied for your role.",
            "access_denied": "Access denied for your role.",
            "unauth": "Please log in first.",
            "welcome": "Welcome",
            "role": "Role",
            "logout": "Logout",
        },
        "fr": {
            "title": "Intelligence Commerciale OS — Connexion",
            "username": "Nom d'utilisateur",
            "password": "Mot de passe",
            "login": "Se connecter",
            "register": "S'inscrire",
            "signup_title": "Créer un compte",
            "role_label": "Sélectionner le rôle",
            "invalid": "Identifiants invalides",
            "exists": "Ce nom d'utilisateur existe déjà",
            "created": "Compte créé avec succès",
            "expired": "Session expirée — veuillez vous reconnecter.",
            "logout_ok": "Déconnexion réussie",
            "denied": "Accès refusé pour votre rôle.",
            "access_denied": "Accès refusé pour votre rôle.",
            "unauth": "Veuillez d'abord vous connecter.",
            "welcome": "Bienvenue",
            "role": "Rôle",
            "logout": "Déconnexion",
        },
    }

    # ── Navigation ──────────────────────────────────────────────────────
    NAV: Dict[str, Dict[str, str]] = {
        "en": {
            "app_title": "🏢 IntelAI",
            "briefing": "Executive Briefing",
            "kpi_center": "KPI Command Center",
            "planning": "Advanced Planning",
            "ingestion": "Data Ingestion",
            "governance": "Governance",
            "kpi": "📊 KPI Command Center",
            "forecast": "🔮 Forecast & Scenarios",
            "risk": "⚠️ Risk Radar",
            "esg": "🌱 ESG & Impact",
            "copilot": "🤖 AI Copilot",
            "data_hub": "📥 Data Hub",
            "settings": "⚙️ Settings",
            "subtitle": "Real-time KPIs • AI-Powered Insights • Strategic Analytics",
            "navigation": "Navigation",
            "system_status": "System Status",
            "logout": "🚪 Logout",
            "welcome": "Welcome",
            "role": "Role",
            "status": "System Status",
            "latest": "Latest Data",
            "periods": "periods available",
            "no_data": "⚠️ No data loaded",
            "kb_items": "knowledge items",
            "kb_empty": "Knowledge base empty",
            "nav_label": "📍 Navigation",
        },
        "fr": {
            "app_title": "🏢 Intelligence Commerciale OS",
            "briefing": "Tableau de bord exécutif",
            "kpi_center": "Centre de commande KPI",
            "planning": "Planification avancée",
            "ingestion": "Ingestion de données",
            "governance": "Gouvernance",
            "kpi": "📊 Centre de commande KPI",
            "forecast": "🔮 Prévisions & Scénarios",
            "risk": "⚠️ Radar de risque",
            "esg": "🌱 ESG & Impact",
            "copilot": "🤖 Copilote IA",
            "data_hub": "📥 Hub de données",
            "settings": "⚙️ Paramètres",
            "subtitle": "KPIs en temps réel • Insights IA • Analyses stratégiques",
            "navigation": "Navigation",
            "system_status": "État du système",
            "logout": "🚪 Déconnexion",
            "welcome": "Bienvenue",
            "role": "Rôle",
            "status": "État du système",
            "latest": "Dernières données",
            "periods": "périodes disponibles",
            "no_data": "⚠️ Aucune donnée chargée",
            "kb_items": "éléments de connaissance",
            "kb_empty": "Base de connaissances vide",
            "nav_label": "📍 Navigation",
        },
    }

    # ── Copilot / Chatbot ───────────────────────────────────────────────
    COPILOT: Dict[str, Dict[str, str]] = {
        "en": {
            "title": "🤖 AI Intelligence Copilot",
            "placeholder": "Ask about your company…",
            "voice_btn": "🎤 Voice Command",
            "listening": "Listening… (Real-time Mode)",
            "thinking": "Analysing…",
            "sources": "Sources",
            "no_answer": "Unable to generate a response.",
            "error": "Error processing request.",
            "lang_prompt": "Reply in English.",
        },
        "fr": {
            "title": "🤖 Copilote IA Intelligence",
            "placeholder": "Posez une question sur votre entreprise…",
            "voice_btn": "🎤 Commande vocale",
            "listening": "Écoute en cours… (Temps réel)",
            "thinking": "Analyse en cours…",
            "sources": "Sources",
            "no_answer": "Impossible de générer une réponse.",
            "error": "Erreur lors du traitement.",
            "lang_prompt": "Répondez en français.",
        },
    }

    # ── Finance ─────────────────────────────────────────────────────────
    FINANCE: Dict[str, Dict[str, str]] = {
        "en": {
            "pl": "Profit & Loss", "bs": "Balance Sheet",
            "cf": "Cash Flow", "gross_margin": "Gross Margin",
            "op_margin": "Operating Margin", "net_margin": "Net Margin",
            "ebitda_margin": "EBITDA Margin", "revenue": "Revenue",
            "cogs": "Cost of Goods Sold", "net_income": "Net Income",
            "health": "Health Index", "risk": "Risk Score",
            "health_index": "Health Index", "risk_score": "Risk Score",
            "esg_rating": "ESG Rating", "simulation": "Monte Carlo Simulation",
            "base_revenue": "Base Revenue", "growth": "Expected Growth (%)",
            "growth_pct": "Expected Monthly Growth (%)",
            "volatility": "Market Volatility", "run_sim": "Run Simulation",
            "sim_done": "Simulation Complete!",
        },
        "fr": {
            "pl": "Compte de résultat", "bs": "Bilan",
            "cf": "Flux de trésorerie", "gross_margin": "Marge brute",
            "op_margin": "Marge opérationnelle", "net_margin": "Marge nette",
            "ebitda_margin": "Marge EBITDA", "revenue": "Chiffre d'affaires",
            "cogs": "Coût des ventes", "net_income": "Résultat net",
            "health": "Indice de santé", "risk": "Score de risque",
            "health_index": "Indice de santé", "risk_score": "Score de risque",
            "esg_rating": "Note ESG", "simulation": "Simulation Monte Carlo",
            "base_revenue": "CA de base", "growth": "Croissance attendue (%)",
            "growth_pct": "Croissance mensuelle attendue (%)",
            "volatility": "Volatilité du marché", "run_sim": "Lancer la simulation",
            "sim_done": "Simulation terminée !",
        },
    }

    # ── Data Hub / Ingestion ────────────────────────────────────────────
    INGESTION: Dict[str, Dict[str, str]] = {
        "en": {
            "title": "📥 Data Ingestion Hub",
            "mode": "Select Ingestion Mode",
            "excel": "Excel / CSV", "excel_csv": "Excel / CSV",
            "ocr": "Invoice / Receipt (OCR)",
            "web": "Web Intelligence", "upload": "Upload file",
            "upload_kpi": "Upload KPI file (CSV/Excel)",
            "upload_invoice": "Upload invoices (handwritten or digital)",
            "processing": "Processing…", "success": "Processed successfully",
            "error": "Error processing file",
            "analysing": "Analysing document…", "ready": "Ready for Ledger",
            "ingest": "Ingest Data", "process": "Process with AI",
            "generate_sample": "Generate Sample Data",
            "web_query": "Search query", "search": "Search",
        },
        "fr": {
            "title": "📥 Hub d'ingestion",
            "mode": "Mode d'ingestion",
            "excel": "Excel / CSV", "excel_csv": "Excel / CSV",
            "ocr": "Facture / Reçu (OCR)",
            "web": "Intelligence Web", "upload": "Téléverser",
            "upload_kpi": "Téléverser un fichier KPI (CSV/Excel)",
            "upload_invoice": "Téléverser des factures",
            "processing": "Traitement…", "success": "Traitement réussi",
            "error": "Erreur de traitement",
            "analysing": "Analyse du document…", "ready": "Prêt pour le grand livre",
            "ingest": "Ingérer les données", "process": "Traiter avec l'IA",
            "generate_sample": "Générer des données d'exemple",
            "web_query": "Requête de recherche", "search": "Rechercher",
        },
    }

    # ── RBAC / Admin ────────────────────────────────────────────────────
    RBAC: Dict[str, Dict[str, str]] = {
        "en": {
            "panel": "Admin Panel", "roles": "Manage Roles",
            "create": "Create Role", "edit": "Edit Role",
            "delete": "Delete Role", "assign": "Assign User",
            "users": "Users", "audit": "Audit Log",
            "success": "Operation successful", "error": "Operation failed",
        },
        "fr": {
            "panel": "Panneau admin", "roles": "Gérer les rôles",
            "create": "Créer un rôle", "edit": "Modifier",
            "delete": "Supprimer", "assign": "Attribuer",
            "users": "Utilisateurs", "audit": "Journal d'audit",
            "success": "Opération réussie", "error": "Opération échouée",
        },
    }

    # ── Common ──────────────────────────────────────────────────────────
    COMMON: Dict[str, Dict[str, str]] = {
        "en": {
            "yes": "Yes", "no": "No", "ok": "OK",
            "cancel": "Cancel", "save": "Save", "delete": "Delete",
            "edit": "Edit", "add": "Add", "back": "Back", "next": "Next",
            "loading": "Loading…", "error": "Error", "success": "Success",
            "warning": "Warning", "confirm": "Confirm",
            "period": "Period", "metric": "Metric", "value": "Value",
            "category": "Category", "segment": "Segment",
            "language": "Language", "english": "English", "french": "Français",
            "no_data": "No data available",
            "latest_data": "Latest Data",
            "periods": "periods",
            "knowledge_items": "knowledge items",
            "kb_empty": "Knowledge base empty",
            "rows_ingested": "rows ingested",
            "processing": "Processing…",
            "done": "Done!",
            "export": "Export",
            "on_track": "On Track",
            "at_risk": "At Risk",
        },
        "fr": {
            "yes": "Oui", "no": "Non", "ok": "OK",
            "cancel": "Annuler", "save": "Enregistrer", "delete": "Supprimer",
            "edit": "Modifier", "add": "Ajouter", "back": "Retour", "next": "Suivant",
            "loading": "Chargement…", "error": "Erreur", "success": "Succès",
            "warning": "Avertissement", "confirm": "Confirmer",
            "period": "Période", "metric": "Métrique", "value": "Valeur",
            "category": "Catégorie", "segment": "Segment",
            "language": "Langue", "english": "English", "french": "Français",
            "no_data": "Aucune donnée disponible",
            "latest_data": "Dernières données",
            "periods": "périodes",
            "knowledge_items": "éléments de connaissance",
            "kb_empty": "Base de connaissances vide",
            "rows_ingested": "lignes ingérées",
            "processing": "Traitement…",
            "done": "Terminé !",
            "export": "Exporter",
            "on_track": "En bonne voie",
            "at_risk": "À risque",
        },
    }

    # ── API ──────────────────────────────────────────────────────────────
    @classmethod
    def set_language(cls, lang: Language) -> None:
        if lang not in ("en", "fr"):
            raise ValueError(f"Unsupported language: {lang}")
        cls._lang = lang

    @classmethod
    def lang(cls) -> Language:
        return cls._lang

    @classmethod
    def get(cls, section: str, key: str, default: str = "") -> str:
        """Retrieve a translated string: ``I18N.get("AUTH", "login")``."""
        try:
            return getattr(cls, section)[cls._lang][key]
        except (AttributeError, KeyError):
            return default or key

    @classmethod
    def section(cls, name: str) -> Dict[str, str]:
        """Return all keys for a section in the current language."""
        try:
            return getattr(cls, name).get(cls._lang, {})
        except AttributeError:
            return {}

# Convenience alias
def t(section: str, key: str, default: str = "") -> str:
    """Shorthand for ``I18N.get(...)``."""
    return I18N.get(section, key, default)
