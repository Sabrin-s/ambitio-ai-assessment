# ⚖️ Legal Document Workspace Engine

An intelligent, decoupled text processing and engineering pipeline designed to ingest messy legal transcripts, perform verifiable grounded retrieval, construct cited summaries, and adaptively learn formatting preferences from live human operator overrides using a localized storage memory matrix.

---

## 🏛️ 1. Short Architecture Overview

The workspace architecture is engineered around 5 highly decoupled, modular layers running in a strict horizontal pipeline

1. Document Processing Layer: Ingests unstructured, messy text inputs, running text normalization routines to strip extra whitespaces, resolve line-break anomalies, and isolate variables for safe downstream computation.

2. Grounded Retrieval Layer: Segments clean text into localized 100-word sliding window chunks, indexing them using a local vector coordinate algorithm. Relevant text evidence is isolated using a mathematical Cosine Similarity Matrix.

3. Draft Generation Layer: Merges retrieved context with historical active layout instructions. It enforces zero-hallucination thresholds by anchoring text drafting strictly to evidence segments and appending precise inline citations ([Source: DOC_REF_X]).

4. Interactive Operator Interface: A localized multi-panel front-end canvas written in Python using Streamlit that hosts execution triggers on the left and a live document editor panel on the right.

5. Adaptive Improvement Learning Core: Intercepts manual operator canvas changes, analyzes structural intent patterns instead of character-level diffs, and saves rules permanently into a local SQLite Database File (operator_feedback.db).

## Brief Write-up of Assumptions and Trade-offs ##
•	Assumption on Raw Document Quality: It is assumed that highly degraded physical scans or messy handwritten PDFs have been pre-processed via optical character recognition frameworks into a messy text transcript block. The pipeline's responsibility is to systematically normalize, parse, and structure this data cleanly for downstream tasks.

•	Trade-off on Semantic Embeddings Execution: To ensure the system runs smoothly out of the box without external API keys, or massive deep-learning model downloads, a localized mathematical hashing engine handles vector space matching. In a live enterprise deployment, this would be replaced with an industrial index model (e.g., ChromaDB, pgvector) alongside dense embeddings (e.g., OpenAI text-embedding-3-small).

•	Intent-Based Rule Learning vs. Raw Text Diffing: The system intentionally avoids standard character-by-character replacements (difflib). Text diffs fail to capture structural patterns (e.g., recognizing that capitalization changes mean an operator prefers uppercase headers globally). The pipeline assumes structural overrides follow an extractable pattern, choosing to interpret intent over raw text differences.

## Sample Input (Messy Ingested Stream) ##
=== AMBITIO CORP AMENDMENT AGREEMENT ===   
!!! CONFIDENTIAL !!! Executed on June 04, 2026.   
Parties Involved: Ambitio AI Systems Inc. and international tech vendors LLC.
Section 4 (Liabilities): Total financial corporate exposure and downstream liability caps 
are restricted strictly to an absolute maximum of $50,000. Text is partially obscured 
here due to ink smudging... End of page record.

## Sample Output #1 (Initial Baseline Draft Generation)##
After an operator modifies section titles to capital letters and updates memory registers, the system updates its behavioral generation natively for all future workflows
### INTERNAL LEGAL MEMO

**1. PARTIES INVOLVED:** Ambitio AI Systems Inc. and international tech vendors LLC [Source: DOC_REF_0_segment_0].
**2. TERM AMENDMENT:** Agreement executed on June 04, 2026 [Source: DOC_REF_0_segment_0].
**3. LIABILITY EXPOSURE:** Total financial corporate exposure and downstream liability caps are restricted strictly to an absolute maximum of $50,000 [Source: DOC_REF_0_segment_0].

## Approach and Results
To measure system performance against the evaluation rubric, the application evaluates four core metrics:
1.	Grounding Accuracy (Hallucination Control): Verifies that 100% of sentences inside the generated draft map to an inspectable data citation tag.
2.	Retrieval Precision (Relevance): Evaluates whether the text segment matched contains the targeted parameters requested.
3.	Data Ingestion Stability: Tracks structural transformations of unformatted text streams into clean string variables.
4.	Learning Optimization Metric: Validates that formatting rules are correctly saved into the SQLite database and applied to future loops.

## How to Use
Step 1: Navigate to the Workspace Directory
Open your terminal, command prompt, or PowerShell, and change directories into your project root folder:

Bash
cd D:\ambitio-ai-assessment

Step 2: Install Required Dependencies
Bash
pip install streamlit

pip install numpy

Step 3: Launch the Pipeline Application
Execute the primary file using Streamlit to initialize your local ecosystem and spin up the frontend dashboard:

streamlit run app.py

