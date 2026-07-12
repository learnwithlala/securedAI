# Secure AI & GenAI Security Architecture (Day 1 & Day 2 Labs)

Welcome to the hands-on lab repository for the **Secure AI & GenAI Architecture** training program. This repository contains the complete set of student lab manuals, automation scripts, and Python source files for both Day 1 and Day 2 of the course.

All scripts are cross-platform and support two modes of operation out-of-the-box:
1. **Simulation Mode (Offline)**: Runs immediately on any computer (including Windows CMD/PowerShell) without requiring active AWS credentials or API keys. Ideal for local practice and demonstration.
2. **Real AWS/API Mode**: Connects directly to live Amazon Bedrock and Anthropic endpoints when credentials are configured.

---

## 📂 Repository Structure

```directory
├── SecureAI_Day1_Lab_Manual.docx  # Detailed Word manual for Day 1 Labs (Lab 1 & 2)
├── SecureAI_Day2_Lab_Manual.docx  # Detailed Word manual for Day 2 Labs (Lab 3 & 4)
├── requirements.txt               # Unified dependencies file for all labs
│
├── ── Day 1: Attack & Guardrails ──────────────────────────────────────────
├── lab1_prompt_injection.py       # Lab 1: Offline/Anthropic Prompt Injection Lab (4 Exercises)
├── lab1_aws_bedrock.py           # Lab 1: Amazon Bedrock Claude Haiku Prompt Injection Lab
├── lab2_guardrails.py            # Lab 2: Automated AWS Bedrock Guardrail Builder & Tester
│
└── ── Day 2: Red-Teaming & Secure Deployment ──────────────────────────────
    ├── lab4_secure_invoke.py     # Lab 4: Secure AWS Bedrock Pipeline Integration
    ├── lab4_rag_rbac.py          # Lab 4: RAG Vector DB Search with Role-Based Access Control
    └── lab4_e2e_test.py          # Lab 4: End-to-End security and RAG pipeline validation
```

---

## ⚡ Quick Start & Prerequisites

### 1. Installation
Install the required dependencies using `pip`:
```bash
pip install -r requirements.txt
```

### 2. Configure AWS Credentials (For Real AWS Mode)
To run Bedrock/Guardrail API operations, install the AWS CLI and configure your IAM user credentials:
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and set default region to: us-east-1
```
*Note: Make sure your AWS user has model access enabled for **Anthropic Claude Haiku** and **Amazon Titan Embeddings** in the Amazon Bedrock Console under "Model Access".*

---

## 🛡️ Running the Labs

### 🧪 Day 1 Lab 1: Prompt Injection Lab
Explore the top vulnerability in the **OWASP LLM Top 10 (LLM01)** by demonstrating Direct Injection, Prompt Leaking, Indirect RAG Document Injection, and Jailbreaking.

* **Offline Simulation Mode:**
  ```bash
  python lab1_prompt_injection.py
  ```
* **Real API Mode (using Anthropic Claude directly):**
  ```bash
  # Linux/Mac
  export ANTHROPIC_API_KEY="your-sk-ant-key"
  # Windows CMD
  set ANTHROPIC_API_KEY="your-sk-ant-key"
  
  python lab1_prompt_injection.py
  ```

### ☁️ Day 1 Lab 1 (AWS Bedrock Version)
Tests prompt injection attacks against a real Amazon Bedrock model endpoint.
```bash
python lab1_aws_bedrock.py
```

### 🧱 Day 1 Lab 2: Building Guardrails
Builds an AWS Bedrock Guardrail. This script automatically configures content filters, sensitive PII block/redaction rules, and topic denial parameters. Once built, it runs side-by-side comparison tests to show how protected endpoints block attacks.
```bash
python lab2_guardrails.py
```
*Note: This script automatically writes the created Guardrail ID to `guardrail_id.txt` so that `lab1_aws_bedrock.py` and `lab4_secure_invoke.py` can load and use it instantly.*

---

### 🚀 Day 2 Lab 4: Secure Bedrock Integration
Loads the custom Guardrail ID and configures low temperature (0.1 for determinism) and token limits to prevent response-inflation attacks.
```bash
python lab4_secure_invoke.py
```

### 🔑 Day 2 Lab 4: RAG with Role-Based Access Control (RBAC)
Demonstrates the implementation of metadata-based RBAC filters over a kNN vector search context retrieve. It shows how to block unauthorized users from extracting sensitive context snippets before sending the prompt to the LLM.
```bash
python lab4_rag_rbac.py
```

### 🏁 Day 2 Lab 4: End-to-End Pipeline Validator
Runs automated positive and negative test cases against the secure pipeline (verifying that normal queries pass and injections/PII/restricted topics are correctly blocked).
```bash
python lab4_e2e_test.py
```

---

## 🎯 Educational Mappings
The exercises in these labs directly map to standard security frameworks:
* **OWASP Top 10 LLM Risks**: Bypassing Controls (`LLM01`), Data Poisoning (`LLM03`), Sensitive Info Leakage (`LLM06`).
* **MITRE ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems)**: Direct Prompt Injection (`AML.T0054`), LLM Prompt Leaking (`AML.T0057`).
* **NIST AI Risk Management Framework (NIST AI RMF)**: Technical controls for Trustworthy AI systems.

---

## 🎓 Authors & Course Information
* **Instructor/Author**: Lalaji ( Top 50 CCISO Hall of Fame)
* **Target Audience**: Security Architects, Cloud Security Engineers, Application Security Professionals, Blue Teams & Red Teams.
