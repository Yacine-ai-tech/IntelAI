"""Static French translations for the glossary (pre-generated, reviewed).
Keeps the FR glossary complete + instant + LLM-independent. term -> {field: fr_text}.
"""

from __future__ import annotations
from typing import Dict

GLOSSARY_FR: Dict[str, Dict[str, str]] = {
    "Revenue": {
        "definition": "Revenu total provenant de la vente de biens ou de services pendant une période, avant déduction de tout coût (première ligne).",
        "benchmark": "La croissance par rapport à la période précédente est plus importante que le montant absolu ; les logiciels SaaS visent 2-3%+ MoM."
    },
    "Gross Margin": {
        "definition": "Partie du revenu restant après le coût direct de livraison du produit (COGS).",
        "benchmark": "Logiciels 70-85% ; >75% est sain. En dessous de 50% exerce une pression sur tout ce qui suit."
    },
    "EBITDA": {
        "definition": "Bénéfice avant intérêts, impôts, dépréciation et amortissement — un indicateur de rentabilité opérationnelle de base.",
        "benchmark": "Positif et en hausse ; la marge EBITDA (EBITDA/Revenu) >20% est solide."
    },
    "Operating Costs": {
        "definition": "Coûts permanents de fonctionnement de l'entreprise (salaires, loyer, logiciels, ventes et marketing) à l'exclusion du COGS.",
        "benchmark": "Devraient augmenter plus lentement que le revenu (effet de levier opérationnel)."
    },
    "Net Profit": {
        "definition": "Ce qui reste après tous les coûts, intérêts et impôts (dernière ligne).",
        "benchmark": "Marge nette >10% est solide pour la plupart des secteurs."
    },
    "Operating Cash Flow": {
        "definition": "Trésorerie générée par les opérations normales — le véritable test pour savoir si l'entreprise s'autofinance.",
        "benchmark": "Positif et en progression ; devrait suivre l'EBITDA dans le temps."
    },
    "Rule of 40": {
        "definition": "Heuristique selon laquelle le taux de croissance d'une entreprise logicielle saine additionné à sa marge bénéficiaire doit être d'au moins 40%.",
        "benchmark": "≥40% sain ; >60% rapporte 2–3× la valorisation. Seuls ~11–30% des SaaS dépassent les 40%."
    },
    "COGS": {
        "definition": "Coût des biens vendus — les coûts directs de production/livraison de ce qui a été vendu pendant la période.",
        "benchmark": "Chiffre d'affaires − COGS = bénéfice brut ; les logiciels maintiennent les COGS bas (marge brute élevée)."
    },
    "Taxes": {
        "definition": "Impôts sur le revenu prélevés sur le bénéfice avant impôts pour la période.",
        "benchmark": "Suivre le taux d'imposition effectif ; déduit pour atteindre le bénéfice net."
    },
    "Free Cash Flow": {
        "definition": "Argent liquide restant après les coûts d'exploitation et les dépenses en capital — l'argent réellement disponible aux investisseurs/réinvestissement.",
        "benchmark": "Positif et en croissance ; marge FCF >10% est forte. Alimente la Règle de 40."
    },
    "Working Capital": {
        "definition": "Coussin de liquidité à court terme — actifs courants moins passifs courants.",
        "benchmark": "Fonds positifs pour les opérations quotidiennes ; surveiller la tendance, et non seulement le niveau."
    },
    "Days Sales Outstanding": {
        "definition": "Nombre moyen de jours pour encaisser de l'argent après une vente — à quelle vitesse les comptes clients se convertissent en argent.",
        "benchmark": "Plus bas libère de l'argent ; <45 jours est sain pour la plupart des B2B."
    },
    "Cash Runway": {
        "definition": "Mois pendant lesquels l'entreprise peut fonctionner au rythme actuel de brûlage de trésorerie avant d'épuiser ses liquidités.",
        "benchmark": "18–24 mois est la norme post-2023 que les investisseurs attendent avant le prochain tour de financement."
    },
    "MRR": {
        "definition": "Revenu récurrent mensuel — revenu d'abonnement prévisible normalisé à un mois.",
        "benchmark": "Suivre le MRR net nouveau (nouveau + extension − churn − contraction)."
    },
    "ARR": {
        "definition": "Revenu récurrent annuel — rythme annuel de revenu récurrent ; l'unité standard du conseil d'administration/de l'investisseur.",
        "benchmark": "Atténue le bruit mensuel ; associer au taux de croissance et au NRR."
    },
    "Customer Count": {
        "definition": "Nombre de clients actifs payants/logos.",
        "benchmark": "Lire en parallèle avec la concentration des revenus et le churn de logos."
    },
    "Churn Rate": {
        "definition": "Taux auquel les clients (churn de logos) ou les revenus (churn de revenus) sont perdus pendant une période.",
        "benchmark": "Mensuel <3% excellent, >7% préoccupant. Suivre le churn de logos ET de revenus."
    },
    "CAC": {
        "definition": "Coût d'acquisition client — coût complet de vente et de marketing pour gagner un nouveau client.",
        "benchmark": "Juger via le remboursement du CAC : <12 mois élite, 15–18 médian."
    },
    "LTV": {
        "definition": "Valeur du client sur toute sa durée de vie — bénéfice de marge brute attendu d'un client sur toute sa durée de vie.",
        "benchmark": "Toujours ajusté en fonction de la marge ; associer au CAC sous forme de ratio."
    },
    "LTV:CAC": {
        "definition": "Rapport entre la valeur sur toute la durée de vie et le coût d'acquisition — efficacité de l'économie de croissance.",
        "benchmark": "Sain 3:1–5:1 ; les meilleures entreprises >4:1."
    },
    "Net Promoter Score": {
        "definition": "Indice de fidélité client basé sur une question ('quelle est la probabilité que vous recommandiez ?', 0–10) ; un indicateur principal de turnover/expansion.",
        "benchmark": "B2B SaaS 30–40 solide ; consommateur 50+ sain."
    },
    "Net Revenue Retention": {
        "definition": "Revenu conservé et augmenté à partir de la base de clients existante (expansion − turnover − contraction).",
        "benchmark": "Entreprise 110–120%+, PME 100–110%. >100% signifie que la base grandit d'elle-même."
    },
    "CAC Payback": {
        "definition": "Mois de bénéfice brut nécessaires pour récupérer le coût d'acquisition d'un client.",
        "benchmark": "<12 mois élite, 15–18 médian ; le véritable test de l'efficacité du CAC."
    },
    "ARPU": {
        "definition": "Revenu moyen par utilisateur/compte — revenu récurrent divisé par les clients actifs.",
        "benchmark": "ARPU croissant signale une vente croisée/puissance de tarification ; lire avec le turnover."
    },
    "Active Users": {
        "definition": "Nombre d'utilisateurs actifs pendant une période (mensuel = MAU, quotidien = DAU) — un signal d'engagement de base.",
        "benchmark": "Ratio DAU/MAU (fidélité) >20% est bon ; >50% est exceptionnel."
    },
    "Headcount": {
        "definition": "Effectif total des employés actifs (souvent exprimé en équivalents temps plein, FTE).",
        "benchmark": "Lire par rapport au chiffre d'affaires par employé et planifier."
    },
    "Turnover Rate": {
        "definition": "Part de la main-d'œuvre qui quitte pendant une période ; segmenter les départs volontaires et involontaires.",
        "benchmark": "Volontaire <10% est bon ; le secteur technologique tourne à 15–20%. Une rétention >85% est saine."
    },
    "Engagement Score": {
        "definition": "Combinaison de l'engagement et de la motivation des employés ; souvent mesuré comme eNPS (NPS des employés).",
        "benchmark": "eNPS >+20 est bon, >+50 est excellent. Dans le monde, seulement ~23% sont engagés."
    },
    "Time to Hire": {
        "definition": "Jours entre l'entrée d'un candidat dans le pipeline et l'acceptation de l'offre (par opposition au temps pour remplir une requête ouverte).",
        "benchmark": "Plus court, cela réduit le coût de vacance ; référencer par rôle ou ancienneté."
    },
    "Training Hours": {
        "definition": "Heures moyennes de formation et de développement par employé — un indicateur préalable d'investissement dans les personnes.",
        "benchmark": "L'augmentation de la formation et du développement est corrélée à la rétention et à la mobilité interne."
    },
    "Open Positions": {
        "definition": "Postes actuellement non pourvus et approuvés — un signal d'écart de capacité et de charge de recrutement.",
        "benchmark": "Lire avec le temps d'embauche et le plan d'affaires."
    },
    "Quality of Hire": {
        "definition": "Valeur en aval des nouveaux embauches (performance, montée en puissance, rétention) liée au canal de sourcing.",
        "benchmark": "Les équipes de meilleures pratiques suivent la QoH pour orienter les dépenses de recrutement."
    },
    "Average Tenure": {
        "definition": "Durée moyenne pendant laquelle les employés sont restés — un signal de rétention et de connaissance institutionnelle.",
        "benchmark": "L'augmentation de l'ancienneté (avec des embauches saines) signale la stabilité ; très élevée peut signaler la stagnation."
    },
    "Cost per Hire": {
        "definition": "Coût complet pour pourvoir un poste (sourcing, agence, recommandation, temps de recruteur).",
        "benchmark": "Référencer par poste/seniorité ; l'augmentation du CPH avec un temps d'embauche lent signale des problèmes de pipeline."
    },
    "Absenteeism Rate": {
        "definition": "Part du temps de travail prévu perdu en raison d'une absence non planifiée — un signal de bien-être et d'engagement.",
        "benchmark": "<3% typique ; les hausses soutenues précèdent souvent l'attrition."
    },
    "Offer Acceptance Rate": {
        "definition": "Part des offres d'emploi que les candidats acceptent — mesure la compétitivité de l'offre et l'expérience du candidat.",
        "benchmark": "85–90%+ est sain ; en dessous de ~80% signale des problèmes de rémunération ou de processus."
    },
    "Internal Mobility Rate": {
        "definition": "Part des postes pourvus par des mobilités internes/promotions plutôt que par des embauches externes.",
        "benchmark": "Une mobilité interne plus élevée est corrélée à la fidélisation et à une réduction des coûts d'embauche."
    },
    "Revenue per Employee": {
        "definition": "Revenu généré par employé à temps plein — le principal indicateur de productivité de la main-d'œuvre.",
        "benchmark": "Dépend du secteur ; une augmentation du RPE indique une mise à l'échelle efficace. Les logiciels SaaS affichent souvent 200 000 $ à 400 000 $+."
    },
    "On-time Delivery": {
        "definition": "Part des commandes livrées à la date promise (OTIF ajoute 'en totalité').",
        "benchmark": "Classe mondiale 95–98 %+."
    },
    "Cycle Time": {
        "definition": "Temps nécessaire pour produire une unité / compléter une série de processus ; la comparaison entre le temps réel et la norme conçue révèle les écarts.",
        "benchmark": "Stable et proche du temps de cycle cible ; surveiller la variance."
    },
    "Defect Rate": {
        "definition": "Part de la production qui ne répond pas aux normes de qualité (inverse du rendement à la première passe).",
        "benchmark": "Objectif de rendement à la première passe 95 %+ (99 %+ pour l'automobile et le médical) → taux de défauts < 5 %."
    },
    "Capacity Utilization": {
        "definition": "Part de la capacité de production disponible qui est réellement utilisée.",
        "benchmark": "Environ 85 % est souvent le point optimal (marge pour les pics et la maintenance)."
    },
    "Production Efficiency": {
        "definition": "Efficacité de production globale — disponibilité × performance × qualité ; le score de productivité de référence.",
        "benchmark": "OEE de classe mondiale ≈ 85 % ; de nombreuses usines se situent entre 40–60 %."
    },
    "Safety Incident Rate": {
        "definition": "Taux d'incidents enregistrables — blessures enregistrables sur le lieu de travail normalisées par rapport aux heures travaillées.",
        "benchmark": "Plus il est bas, mieux c'est ; examiné mensuellement en tant qu'indicateur stratégique de sécurité."
    },
    "First Pass Yield": {
        "definition": "Unités qui passent sans reprise ou rebut au premier essai.",
        "benchmark": "95 % + dans la plupart des industries ; 99 % + dans l'industrie automobile/médicale."
    },
    "Quality Rate": {
        "definition": "Part de la production qui répond aux spécifications de qualité (la composante qualité de l'OEE ; inverse du taux de défauts).",
        "benchmark": "97 % + pour la plupart des industries ; 99 % + dans l'industrie automobile/médicale."
    },
    "Throughput": {
        "definition": "Volume d'unités produites/traitées par unité de temps — capacité de production brute en action.",
        "benchmark": "Lire par rapport au temps de takt et à la demande ; la stabilité est aussi importante que le niveau."
    },
    "Unplanned Downtime": {
        "definition": "Heures pendant lesquelles les équipements/lignes sont arrêtés de manière inattendue — le plus grand frein à la disponibilité de l'OEE.",
        "benchmark": "Plus il est bas, mieux c'est ; la maintenance prédictive vise à atteindre des arrêts imprévus proches de zéro."
    },
    "Cost per Unit": {
        "definition": "Coût complet pour produire une unité de production — relie les opérations à la marge brute.",
        "benchmark": "Diminue avec l'échelle et l'efficacité ; l'augmentation du coût par unité érode la marge."
    },
    "Schedule Adherence": {
        "definition": "Détermination de la proximité entre la production réelle et la planification/prévision — achèvement à temps des travaux planifiés.",
        "benchmark": "90%+ indique un plan fiable et équilibré."
    },
    "Scrap Rate": {
        "definition": "Partie du matériau/production rejetée comme impropre à l'usage — déchets directs et coûts.",
        "benchmark": "Plus bas est meilleur ; les objectifs lean visent une réduction continue vers <2%."
    },
    "System Uptime": {
        "definition": "Pourcentage de temps pendant lequel les systèmes sont disponibles, souvent exprimé en 'nines'.",
        "benchmark": "99,9% ('trois nines') ≈ 8,8h/an de temps d'arrêt ; 99,99% est solide."
    },
    "Mean Time to Resolution": {
        "definition": "Temps moyen pour se remettre d'un incident/déploiement échoué — la métrique DORA la plus fiable à l'ère de l'IA.",
        "benchmark": "Les équipes d'élite se rétablissent en <1 heure."
    },
    "Security Incidents": {
        "definition": "Nombre d'événements de sécurité confirmés (failles, intrusions, violations de politique) pendant une période.",
        "benchmark": "Tendance vers zéro ; associez-le au temps de détection/réponse."
    },
    "Cloud Cost per User": {
        "definition": "Dépenses d'infrastructure/nuage divisées par les utilisateurs actifs — une métrique d'unités économiques FinOps.",
        "benchmark": "Devrait diminuer à mesure de l'échelle (économies d'échelle)."
    },
    "Deployment Frequency": {
        "definition": "Fréquence à laquelle le code est expédié en production — une métrique de throughput DORA.",
        "benchmark": "Elite : à la demande (plusieurs/jour)."
    },
    "IT Satisfaction": {
        "definition": "Satisfaction interne à l'égard des services/outils IT (un score d'expérience développeur ou employé).",
        "benchmark": "Un score plus élevé reflète la santé de la plateforme/DevEx."
    },
    "Change Failure Rate": {
        "definition": "Part des déploiements qui provoquent une défaillance nécessitant un rollback/patch urgent — une métrique de stabilité DORA.",
        "benchmark": "Elite 0–15 % ; les meilleures équipes 2026 < 0,5 %. "
    },
    "Lead Time for Changes": {
        "definition": "Temps entre l'engagement de code et son exécution en production — une métrique de vitesse DORA.",
        "benchmark": "Elite : < 1 heure."
    },
    "Critical Incidents": {
        "definition": "Nombre d'incidents de gravité 1 (panne majeure / faille de sécurité) pendant la période.",
        "benchmark": "Tendance vers zéro ; chaque incident justifie une analyse post-mortem sans reproche."
    },
    "Cloud Spend": {
        "definition": "Dépense totale dans le cloud/infrastructure pour la période — le principal indicateur de coût FinOps.",
        "benchmark": "Devrait augmenter plus lentement que l'utilisation/le chiffre d'affaires ; surveiller le coût unitaire (dépense par utilisateur)."
    },
    "SLA Compliance": {
        "definition": "Part des objectifs d'accord de niveau de service (disponibilité/réponse/résolution) effectivement atteints.",
        "benchmark": "95–99%+ en fonction du niveau ; les manques déclenchent des crédits et un risque d'abandon."
    },
    "Security Score": {
        "definition": "Évaluation composite de la posture de sécurité (correction, vulnérabilités, contrôles, configuration) sur une échelle de 0 à 100.",
        "benchmark": "Plus le score est élevé, mieux c'est ; associer aux tendances des vulnérabilités ouvertes et des incidents."
    },
    "Inventory Turnover": {
        "definition": "Nombre de fois où l'inventaire est vendu et remplacé au cours d'une période — efficacité du capital du stock.",
        "benchmark": "Plus le score est élevé, plus le stock est lean et meilleur est le flux de trésorerie (dépend du secteur)."
    },
    "Order Accuracy": {
        "definition": "Part des commandes sortantes exécutées sans erreur (article/quantité/destination corrects).",
        "benchmark": "Ciblez 95%+ pour réduire les retours et les coûts."
    },
    "Freight Cost per Unit": {
        "definition": "Coût de transport moyen pour expédier une unité — relie l'exécution logistique au compte de résultat.",
        "benchmark": "Réduisez les coûts via l'optimisation du mode, du corridor, du transporteur et de l'emballage."
    },
    "Warehouse Utilization": {
        "definition": "Partie de l'espace/capacité d'entrepôt utilisable réellement utilisée.",
        "benchmark": "~80–85% équilibre la densité avec l'efficacité de prélèvement."
    },
    "Last Mile Delivery Time": {
        "definition": "Délai de livraison pour l'étape finale de livraison au client — un coût et un facteur d'expérience client majeur.",
        "benchmark": "Plus rapide + fiable ; l'étape la plus coûteuse de l'exécution."
    },
    "Returns Rate": {
        "definition": "Partie des commandes expédiées retournées par les clients.",
        "benchmark": "Plus bas est meilleur ; les pointes signalent des problèmes de qualité/ajustement/attente."
    },
    "Perfect Order Rate": {
        "definition": "Partie des commandes livrées à temps, complètes, non endommagées et avec une documentation correcte.",
        "benchmark": "L'étalon-or composite ; 95%+ est solide."
    },
    "Days Inventory Outstanding": {
        "definition": "Nombre moyen de jours pendant lesquels l'inventaire est détenu avant la vente — la vue inverse du roulement.",
        "benchmark": "Plus bas = conversion de trésorerie plus rapide (dépendant du secteur)."
    },
    "On-Time Delivery Rate": {
        "definition": "Partie des commandes livrées à la date promise — la métrique de fiabilité d'exécution de base.",
        "benchmark": "Classe mondiale 95–98%+ ; l'un des principaux facteurs de satisfaction client."
    },
    "Fill Rate": {
        "definition": "Part de la demande satisfaite à partir du stock à la première tentative (remplissage de commande/ligne/unité).",
        "benchmark": "95%+ équilibre le niveau de service avec le coût d'inventaire."
    },
    "Stockout Rate": {
        "definition": "Part de la demande ou des SKUs indisponibles lorsqu'ils sont souhaités — ventes perdues et préjudice pour l'expérience client.",
        "benchmark": "<2–3%; le coût direct de la sous-approvisionnement."
    },
    "Carrying Cost": {
        "definition": "Coût total de détention d'inventaire (capital, stockage, assurance, obsolescence).",
        "benchmark": "Un coût plus faible libère le capital de travail; compromis avec le risque de rupture de stock."
    },
    "Avg Lead Time": {
        "definition": "Temps moyen entre la passation de commande et la livraison — vitesse de réalisation de bout en bout.",
        "benchmark": "Plus court + constant; la variabilité nuit autant que la moyenne."
    },
    "Carbon Emissions (tCO2)": {
        "definition": "Émissions de gaz à effet de serre en tonnes d'équivalent CO2 à travers la portée 1 (direct), 2 (énergie achetée) et 3 (chaîne de valeur).",
        "benchmark": "Sous CSRD/ESRS E1, la divulgation de la portée 1-3 est obligatoire dans l'UE à partir de 2026."
    },
    "Renewable Energy %": {
        "definition": "Part de la consommation d'énergie totale issue des sources renouvelables.",
        "benchmark": "Une part croissante réduit les émissions de la portée 2; de nombreux objectifs visent 100% d'ici 2030."
    },
    "Water Consumption (m3)": {
        "definition": "Consommation totale d'eau douce (en mètres cubes) — un indicateur clé de ressource environnementale (ESRS E3).",
        "benchmark": "Réduire l'intensité par unité de production ; matière dans les zones soumises à une pression sur les ressources en eau."
    },
    "Waste Recycled %": {
        "definition": "Part des déchets détournés des décharges via le recyclage/réutilisation (économie circulaire, ESRS E5).",
        "benchmark": "Plus élevé = performance plus forte en économie circulaire."
    },
    "Diversity Score": {
        "definition": "Indice composite de diversité et d'inclusion de la main-d'œuvre (genre, ethnicité, écart de rémunération) — pilier social (ESRS S1).",
        "benchmark": "Plus élevé reflète une main-d'œuvre inclusive ; divulguer la représentation et les écarts de rémunération."
    },
    "Board Diversity %": {
        "definition": "Part des sièges au conseil d'administration détenus par des groupes sous-représentés — pilier de gouvernance.",
        "benchmark": "De nombreux cadres visent une diversité de genre ≥30–40%."
    },
    "Scope 1 / 2 / 3": {
        "definition": "Frontières d'émission du protocole GHG : Scope 1 = direct (sources détenues) ; Scope 2 = énergie achetée ; Scope 3 = toutes les autres émissions de la chaîne de valeur (généralement la plus importante).",
        "benchmark": "La Scope 3 est obligatoire dans le cadre du CSRD en utilisant le protocole GHG comme base."
    },
    "CSRD": {
        "definition": "Directive européenne sur la déclaration de durabilité des entreprises — exige une déclaration détaillée et auditée sur la durabilité pour 50 000 entreprises et plus.",
        "benchmark": "Déclaration sur les normes ESRS (E1 climat est toujours exigé) ; mise en œuvre progressive de 2024 à 2028."
    },
    "Double Materiality": {
        "definition": "Principe CSRD : divulguer à la fois comment les questions de durabilité affectent l'entreprise (financière) et comment l'entreprise affecte les personnes/la planète (impact).",
        "benchmark": "Détermine les sujets que une entreprise doit déclarer sous ESRS."
    },
    "ESG Score": {
        "definition": "Nota composite de 0 à 100 qui combine les performances environnementale, sociale et de gouvernance.",
        "benchmark": "Plus le score est élevé, mieux c'est ; la méthodologie varie selon l'organisme de notation — divulguer les bases."
    },
    "Scope 1 Emissions": {
        "definition": "Émissions directes de GES provenant de sources détenues/contrôlées (combustion, véhicules d'entreprise, processus).",
        "benchmark": "Obligatoire en vertu de la CSRD/ESRS E1 ; la portée la plus directement contrôlable."
    },
    "Scope 2 Emissions": {
        "definition": "Émissions indirectes de GES provenant de l'énergie achetée (électricité, vapeur, chauffage/rafraîchissement).",
        "benchmark": "Réduites le plus rapidement par l'approvisionnement en énergies renouvelables ; obligatoire en vertu de la CSRD."
    },
    "Scope 3 Emissions": {
        "definition": "Toutes les autres émissions de la chaîne de valeur (fournisseurs, logistique, utilisation des produits, déplacements) — généralement la part la plus importante.",
        "benchmark": "Souvent 70-90 % de l'empreinte ; la divulgation de la portée 3 est maintenant obligatoire en vertu de la CSRD."
    },
    "Emissions Intensity": {
        "definition": "Émissions normalisées à la taille de l'entreprise (par unité de chiffre d'affaires/production) — permet une comparaison équitable et une déconnexion.",
        "benchmark": "Une intensité décroissante montre une déconnexion des émissions de la croissance."
    },
    "Gender Pay Gap": {
        "definition": "Différence entre les salaires moyens entre les genres — une divulgation de base du pilier social (ESRS S1).",
        "benchmark": "Vers 0 % ; divulgation obligatoire en vertu du CSRD et de la directive de transparence salariale de l'UE."
    },
    "Community Investment": {
        "definition": "Dépenses/contributions aux programmes communautaires et sociaux — un indicateur de engagement du pilier social.",
        "benchmark": "Souvent évalué en pourcentage du bénéfice avant impôt ; faire rapport des résultats, et non seulement des dépenses."
    },
    "Risk Score": {
        "definition": "Score composite de santé des risques 0-100 qui combine la volatilité des revenus, le nombre d'anomalies et la concentration.",
        "benchmark": "≥70 Faible risque, 50-70 Risque modéré, <50 Risque élevé."
    },
    "Anomaly Detection": {
        "definition": "Détection statistique des lectures de métriques qui s'écartent fortement de leur tendance (par exemple, une baisse des revenus ou une augmentation de l'abandon).",
        "benchmark": "Chaque anomalie est un élément à surveiller pour enquêter."
    },
    "KPI": {
        "definition": "Indicateur de performance clé — une mesure quantifiée qui suit les progrès par rapport à un objectif.",
        "benchmark": "Les bons KPI sont spécifiques, comparables dans le temps et liés à une décision."
    },
    "RAG": {
        "definition": "Génération augmentée de récupération — l'IA récupère d'abord vos données/documents réels, puis répond à partir de ces preuves (avec des citations) au lieu de la mémoire.",
        "benchmark": "Réduit les hallucinations ; la norme 2026 est hybride + reclassage + graphique."
    },
    "Persona-Routed RAG": {
        "definition": "L'approche d'IntelAI : le copilote adopte une personnalité de rôle (PDG/DGF/…) qui définit les données qu'il peut lire (RBAC) et la façon dont il répond — ancré, approprié au rôle, avec références.",
        "benchmark": "Combines le contrôle d'accès avec la récupération pour des réponses sûres et pertinentes."
    },
    "GraphRAG": {
        "definition": "Récupération sur un graphique d'entités/relations (et non seulement des fragments de texte) afin que l'IA puisse répondre à des questions de relations multi-étapes à travers l'ensemble d'indicateurs clés de performance (KPI).",
        "benchmark": "Knowledge-graph RAG a réduit les hallucinations d'environ 62 % dans les benchmarks de production 2026."
    },
    "Hybrid Retrieval": {
        "definition": "Combinaison de la recherche vectorielle dense (sémantique) avec la recherche de mots clés BM25, fusionnées (RRF), pour capturer à la fois le sens et les termes exacts.",
        "benchmark": "La référence par défaut pour 2026 ; surpasse chaque méthode utilisée séparément."
    },
    "Reranking": {
        "definition": "Un réencodeur réévalue les candidats les plus récupérés pour que les preuves les plus pertinentes soient réellement utilisées — empêche les réponses confiantes provenant de premières récupérations faibles.",
        "benchmark": "Le réévaluation du réencodeur/critique est la norme pour l'ancrage en 2026."
    },
    "Groundedness": {
        "definition": "Détermine si chaque affirmation dans une réponse est étayée par les sources récupérées — la mesure anti-hallucination de base.",
        "benchmark": "IntelAI évalue ses performances en fonction de l'ancrage (citer ou ne pas affirmer)."
    }
}
