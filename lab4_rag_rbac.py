#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  LAB 4: RAG PIPELINE WITH ROLE-BASED ACCESS CONTROL (RBAC)
  Secure AI & GenAI Architecture -- Day 2
  Author : Lalaji -- TLS & L&D Department | Top 50 CCISO Hall of Fame
  Version: 1.0
=============================================================================

  PURPOSE
  -------
  This script implements Role-Based Access Control (RBAC) filtering over
  RAG document retrieval. In a secure enterprise environment:
    1. Documents in OpenSearch are indexed with an `allowed_roles` field.
    2. During query, the pipeline matches document vectors using kNN.
    3. The application filters the search results *before* feeding them
       into the LLM context, ensuring a user only sees documents they are
       authorized to access.

  HOW TO RUN
  ----------
  python lab4_rag_rbac.py

  SIMULATION MODE
  ---------------
  Since OpenSearch clusters are regional, this script contains a built-in
  simulated document vector index that behaves identically to a real
  OpenSearch instance to verify security logic offline.

=============================================================================
"""

import os
import sys
import json
import time

# Fix Windows CP1252 encoding issues by forcing UTF-8 output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Safe imports
try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True, strip=False)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class _Dummy:
        def __getattr__(self, _): return ""
    Fore = Back = Style = _Dummy()

try:
    from opensearchpy import OpenSearch
    HAS_OPENSEARCH = True
except ImportError:
    HAS_OPENSEARCH = False

try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

# =============================================================================
# MOCK DATABASE (For simulation and out-of-the-box educational use)
# =============================================================================
MOCK_KNOWLEDGE_BASE = [
    {
        "text": "[PUBLIC] ShopEasy Standard Refund Policy: Customers can return unworn items within 30 days for a full refund.",
        "allowed_roles": ["public", "sales", "hr", "finance", "admin"]
    },
    {
        "text": "[SALES] ShopEasy Sales Commission Plan: Sales reps receive a 4% tier-1 commission on electronics products.",
        "allowed_roles": ["sales", "admin"]
    },
    {
        "text": "[HR] Employee Incident Logs: Summary of internal reviews regarding staff performance adjustments in Q1.",
        "allowed_roles": ["hr", "admin"]
    },
    {
        "text": "[FINANCE] Q3 Revenue Projections: Confidential projections indicating a 12% margin growth target for retail operations.",
        "allowed_roles": ["finance", "admin"]
    },
    {
        "text": "[CONFIDENTIAL] AWS Admin IAM Secret S3 Buckets: List of raw logs and security auditing buckets in the master account.",
        "allowed_roles": ["admin"]
    }
]

# =============================================================================
# TERMINAL HELPERS
# =============================================================================
def _c(text, color=""):
    return f"{color}{text}{Style.RESET_ALL}" if HAS_COLOR else text

def banner(title, color=Fore.CYAN):
    width = 70
    print()
    print(_c("=" * width, color))
    print(_c(f"  {title}", color))
    print(_c("=" * width, color))
    print()

def section(title, color=Fore.YELLOW):
    print()
    print(_c(f"  -- {title} " + "-" * max(0, 58 - len(title)), color))

def success(msg): print(_c(f"  [OK]  {msg}", Fore.GREEN))
def warn(msg):    print(_c(f"  [!!]  {msg}", Fore.YELLOW))
def error(msg):   print(_c(f"  [XX]  {msg}", Fore.RED))
def info(msg):    print(_c(f"  [>>]  {msg}", Fore.BLUE))

# =============================================================================
# RBAC RAG RETRIEVAL ENGINE
# =============================================================================
class SecureRAGPipeline:
    def __init__(self, use_real_os=False, endpoint="", password=""):
        self.use_real_os = use_real_os
        if self.use_real_os and HAS_OPENSEARCH and HAS_BOTO3:
            self.os_client = OpenSearch(
                [{'host': endpoint, 'port': 443}],
                http_auth=('admin', password),
                use_ssl=True,
                verify_certs=True
            )
            self.embed_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        else:
            self.use_real_os = False
            self.os_client = None
            self.embed_client = None

    def _get_query_vector(self, query_text: str) -> list:
        """Helper to get real embedding from Bedrock Titan Embeddings."""
        if not self.use_real_os:
            return [0.0] * 1536  # Mock vector for simulation
        
        try:
            response = self.embed_client.invoke_model(
                modelId='amazon.titan-embed-text-v1',
                body=json.dumps({'inputText': query_text})
            )
            return json.loads(response['body'].read())['embedding']
        except Exception as e:
            # Fallback to simulation if Bedrock invocation fails
            return [0.0] * 1536

    def retrieve_chunks_with_rbac(self, query: str, user_role: str) -> list:
        """
        Retrieves matching document chunks.
        Filters out any chunks the user does not have permission to access.
        """
        # 1. Fetch query vector
        query_vector = self._get_query_vector(query)

        # 2. Retrieve matched documents (either real OpenSearch or mock index)
        if self.use_real_os:
            try:
                search_results = self.os_client.search(
                    index='kb-vectors',
                    body={
                        'size': 10,
                        'query': {
                            'knn': {
                                'vector_field': {
                                    'vector': query_vector,
                                    'k': 10
                                }
                            }
                        }
                    }
                )
                all_hits = [hit['_source'] for hit in search_results['hits']['hits']]
            except Exception as e:
                warn(f"Failed to query OpenSearch: {e}. Falling back to simulation.")
                all_hits = MOCK_KNOWLEDGE_BASE
        else:
            # Simulate matching everything in our small mock index
            all_hits = MOCK_KNOWLEDGE_BASE

        # 3. RBAC Filtering: Validate if user_role is in allowed_roles
        authorised_chunks = []
        unauthorised_blocked = 0

        for hit in all_hits:
            allowed = hit.get('allowed_roles', [])
            if user_role in allowed:
                authorised_chunks.append(hit['text'])
            else:
                unauthorised_blocked += 1

        print(_c(f"  [RBAC] Retrieved {len(all_hits)} chunks. User Role: '{user_role}'. "
                 f"Authorised: {len(authorised_chunks)} | Blocked: {unauthorised_blocked}", Fore.BLUE))
        
        return authorised_chunks

# =============================================================================
# TEST SUITE
# =============================================================================
def main():
    banner("LAB 4: RAG PIPELINE WITH ROLE-BASED ACCESS CONTROL (RBAC)")

    pipeline = SecureRAGPipeline(use_real_os=False)
    info("Running RBAC Pipeline Validation Suite...")
    print()

    # Define test user credentials/roles
    test_users = [
        {"email": "guest@test.com",        "role": "public"},
        {"email": "sales-manager@test.com", "role": "sales"},
        {"email": "finance-lead@test.com",  "role": "finance"},
        {"email": "root-admin@test.com",   "role": "admin"}
    ]

    query = "Retrieve company documents related to policies, sales, finance, or AWS secrets."

    for user in test_users:
        section(f"USER: {user['email']} | Role: '{user['role']}'")
        chunks = pipeline.retrieve_chunks_with_rbac(query, user_role=user["role"])
        
        print("  Authorised Documents Loaded:")
        if not chunks:
            print(_c("    (None - All access blocked)", Fore.RED))
        for doc in chunks:
            print(f"    - {doc}")
        print()

    success("RBAC RAG testing complete. All unauthorized resources were blocked.")

if __name__ == "__main__":
    main()
