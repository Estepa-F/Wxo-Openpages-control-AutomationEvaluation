<h1 align="center">watsonx Orchestrate × OpenPages — AI Control Evaluation</h1>
<p align="center">
<strong>An agentic AI demo for Governance, Risk &amp; Compliance.<br>
  One click on a control. A justified verdict. The auditor stays in charge.</strong>
</p>
<!-- BADGES -->
<p align="center">
<img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
<img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
<img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python">
<img src="https://img.shields.io/badge/IBM-watsonx_Orchestrate-052FAD.svg?logo=ibm&logoColor=white" alt="IBM watsonx Orchestrate">
<img src="https://img.shields.io/badge/IBM-OpenPages-052FAD.svg?logo=ibm&logoColor=white" alt="IBM OpenPages">
<img src="https://img.shields.io/badge/IBM-Bob-052FAD.svg?logo=ibm&logoColor=white" alt="IBM Bob">
</p>
<!-- CTA -->
<p align="center">
  <a href="https://www.linkedin.com/in/estepa/">
<img src="https://img.shields.io/badge/💬_Discuss_on_LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="Discuss on LinkedIn" height="50">
</a>
</p>

A watsonx Orchestrate demo project that evaluates the **operating effectiveness** of internal
controls stored in IBM OpenPages.

The project brings together:
- **IBM OpenPages** as the GRC system (controls, issues, action plans)
- **IBM watsonx Orchestrate** for the control evaluation agent
- **IBM Bob** with the OpenPages MCP server, to build the solution and run audit analyses

## 🎯 The problem

Testing the operating effectiveness of controls is slow and repetitive:

- 📄 the auditor reads the control description and gathers evidence from several systems (ERP, IAM, HR)
- 🔍 runs the test (three-way match, access review, segregation of duties...)
- ✍️ writes a conclusion and a justification by hand in OpenPages
- 🔁 and repeats it for every control, every campaign

The result: hours per control, uneven justifications, and contradictions between first-line
self-assessments and second-line reviews that are spotted late.

## 💡 The solution

An **AI insights action** directly on the OpenPages control:

- **One click** under the control description calls a watsonx Orchestrate agent
- The agent runs a **test tool** and returns a status — `Effective`, `Ineffective` or
  `Not Determined` — with an **evidence-based explanation**
- The **verdict is computed in code**, not improvised by the LLM, so it is reproducible
- The auditor **reviews and applies** the suggestion: the human stays in the loop

Two more scenarios with **IBM Bob** and the OpenPages MCP server: an HR / ERP access
reconciliation that updates the control, and a second-line action plan assigned to the first line.

> The test tool is a **stub** that returns realistic simulated results. Replace it with real
> data sources without changing the agent or OpenPages.

## 🏗️ Architecture

```
            ┌──────────────────── IBM OpenPages ────────────────────┐
            │  Control ── Description ──▶ [Evaluate (AI)] button    │
            │                                │          ▲           │
            │              Custom ML Model + Extension  │ Set fields│
            └────────────────────────────────┼──────────┼───────────┘
                                             ▼          │ {"OperatingEffectiveness", "Explanation"}
            ┌──────────────── watsonx Orchestrate ───────────────────┐
            │  Control_Evaluation_Agent ──▶ simulate_control_test    │
            └────────────────────────────────────────────────────────┘

            ┌──────── IBM Bob ────────┐        ┌──── OpenPages MCP ────┐
            │ build · deploy · test   │ ─────▶ │ read / upsert objects │
            │ HR/ERP reconciliation   │        │ (human approval)      │
            └─────────────────────────┘        └───────────────────────┘
```

Details: [`docs/architecture.md`](docs/architecture.md).

## Project structure

- [`agents/`](agents/): Orchestrate agent definition
- [`tools/`](tools/): Python test tool called by the agent
- [`scripts/`](scripts/): setup, deployment, end-to-end test and HR / ERP reconciliation scripts
- [`openpages/`](openpages/): OpenAPI spec for the OpenPages Extension
- [`bob/`](bob/): instructions and prompts for IBM Bob
- [`data/`](data/): fictional HR and ERP extracts
- [`tests/`](tests/): offline unit tests and end-to-end test cases
- [`docs/`](docs/): guides

## Quick start

### 1. Prepare the environment

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install ibm-watsonx-orchestrate -r requirements-dev.txt
cp .env.sdk.exemple .env.sdk      # then edit it
```

### Variables to edit in [`.env.sdk.exemple`](.env.sdk.exemple)

Whoever installs the project creates their own local `.env.sdk` file and replaces the
example values with their own information.

#### watsonx Orchestrate
- `WO_INSTANCE_ALIAS`: local alias of the watsonx Orchestrate environment
- `WO_INSTANCE`: watsonx Orchestrate instance URL
- `WO_API_KEY`: watsonx Orchestrate API key

#### OpenPages MCP (optional, for Bob)
- `OPENPAGES_MCP_URL`: URL of the OpenPages MCP server

### 2. Deploy the project

```bash
./scripts/configure_environment.sh
./scripts/deploy_complete.sh
```

### 3. Test

```bash
python3 -m pytest -q tests                 # offline
python scripts/test_agent.py --repeat 5    # deployed agent, prints its ID
```

### 4. Connect OpenPages

Create the Extension, the Custom Machine Learning Model and attach it to the control view:
[`docs/openpages-integration.md`](docs/openpages-integration.md).

## Documentation

### Per-folder documentation

- [`agents/README.md`](agents/README.md)
- [`tools/README.md`](tools/README.md)
- [`scripts/README.md`](scripts/README.md)
- [`openpages/README.md`](openpages/README.md)
- [`bob/README.md`](bob/README.md)
- [`data/README.md`](data/README.md)

### Detailed guides in [`docs/`](docs/)

- [`docs/installation.md`](docs/installation.md) — installation and deployment guide
- [`docs/architecture.md`](docs/architecture.md) — architecture and data flow
- [`docs/openpages-integration.md`](docs/openpages-integration.md) — Extension, Custom ML Model and view configuration
- [`docs/patterns.md`](docs/patterns.md) — design patterns used in the project
- [`docs/scenario-demo.md`](docs/scenario-demo.md) — full demo scenario (3 scenarios)
- [`docs/expected-hr-erp-result.md`](docs/expected-hr-erp-result.md) — expected HR / ERP reconciliation output

## 🎥 External resources

- 💼 [LinkedIn profile](https://www.linkedin.com/in/estepa/)

## ⚖️ License

This project is distributed under the MIT license. See [LICENSE](LICENSE) for details.

```
MIT License
Copyright (c) 2026 François Estepa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction [...]
```

## 🙏 Credits

Built with:
- [IBM watsonx Orchestrate](https://www.ibm.com/products/watsonx-orchestrate) and its [ADK](https://developer.watson-orchestrate.ibm.com/)
- [IBM OpenPages](https://www.ibm.com/products/openpages)
- IBM Bob and the OpenPages MCP server

---

<p align="center">
  ⭐ If this project inspired you, give the repo a star. It helps other architects find it.<br>
  💬 Questions? Open an issue or reach out on <a href="https://www.linkedin.com/in/estepa/">LinkedIn</a>.
</p>
