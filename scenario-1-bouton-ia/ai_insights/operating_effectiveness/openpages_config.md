# Branchement dans OpenPages (bouton AI Insights sur un Control)

Référence : documentation IBM OpenPages (Extensions, Custom Machine Learning Models) et
[ibm-openpages-generating-doc](https://github.com/jpradier/ibm-openpages-generating-doc).

## 1. Extension (Administration → Integrations → Extensions)
- Nouvelle extension, importer `ai_insights/wxo-openapi-control-evaluation.yaml`
  (remplacer `<region>` et `<instance-id>` par ceux de votre instance).
- Authentification : IBM Cloud IAM, avec la clé API `WXO_API_KEY` du `.env`.
- Dans le YAML, remplacer `<AGENT_ID>` par l'ID de l'agent
  (affiché en tête de `python tests/run_tests.py`), ou le saisir dans le mapping ci-dessous.

## 2. Custom Machine Learning Model
- Model access : Watson service type = **Extension**, Extension = celle créée en 1.
- Operation : **Chat with an agent** (`POST /v1/orchestrate/{agent_id}/chat/completions`).
- Input type : **Object fields** — Object type : **Control** (`SOXControl`).

Mapping des entrées (model input field → valeur OpenPages) :

| Model input field | Valeur |
|---|---|
| `agent_id` | ID de `Control_Evaluation_Agent` |
| `stream` | `false` (obligatoire pour OpenPages) |
| `messages[0].role` | `user` |
| `messages[0].content` | le champ **Description** du contrôle |

## 3. Outputs — Insight type : Set fields
Deux sorties, chacune avec une expression JSONata :

| Output label | JSONata | Target field |
|---|---|---|
| Operating Effectiveness | `$eval(choices[0].message.content).OperatingEffectiveness` | `OPSS-Ctl:Operating Effectiveness` (enum : Effective / Ineffective / Not Determined) |
| Explication | `$eval(choices[0].message.content).Explanation` | `OPSS-Ctl-Cert:OpEffExplain` (« Control Operating Effectively Explanation ») |

Champ d'explication : `OpEffExplain` est un STRING_TYPE, dont la longueur maximale est à vérifier
(l'agent produit jusqu'à 1 200 caractères). S'il est trop court, utiliser
`OPSS-FCM-cert:Operating Effectiveness Description` (LARGE_STRING_TYPE, sans limite).

ID de l'agent (à renseigner dans la spec ; affiché par `python tests/run_tests.py`) : `<AGENT_ID>`

`$eval` transforme le texte JSON renvoyé par l'agent en objet.
**À tester en premier** : si OpenPages refuse `$eval`, renvoyer d'abord
`choices[0].message.content` brut dans un champ texte pour voir ce qui arrive.

Les noms techniques des deux champs cibles sont à relever avec Bob (voir README, étape 2).

## 4. Bouton
View Designer → vue Task View du Control → **Add AI insights button** →
sélectionner le Custom ML Model → Publier.
