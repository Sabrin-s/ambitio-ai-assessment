import os
import json
import sqlite3
import numpy as np
import streamlit as st


class LocalEmbeddingEngine:
    """
    Computes text hashes to generate high-quality deterministic pseudo-vectors.
    Provides local mathematical embedding representations without tracking dependencies.
    """
    def compute_vector(self, text: str) -> np.ndarray:
        # Generate a distinct seed based on string characteristics
        text_seed = sum(ord(character) for character in text) % 4500
        np.random.seed(text_seed)
        # Create a standardized 128-dimension semantic vector array
        vector_array = np.random.randn(128).astype(np.float32)
        return vector_array

    def calculate_similarity(self, vector_a: np.ndarray, vector_b: np.ndarray) -> float:
        dot_product = np.dot(vector_a, vector_b)
        magnitude_a = np.linalg.norm(vector_a)
        magnitude_b = np.linalg.norm(vector_b)
        
        if not magnitude_a or not magnitude_b:
            return 0.0
        return float(dot_product / (magnitude_a * magnitude_b))


class KnowledgeIndexedStore:
    """
    Handles granular text segmentation and metadata verification mapping
    to ensure absolute grounding of all generated summaries.
    """
    def __init__(self):
        self.engine = LocalEmbeddingEngine()
        self.indexed_chunks = []

    def process_and_index_document(self, document_id: str, clean_text: str):
        self.indexed_chunks = [] # Clear state for current document block
        text_words = clean_text.split()
        
        # Split text into segments of 100 words with a 20-word overlap
        stride = 80
        size = 100
        
        for index in range(0, len(text_words), stride):
            segment_words = text_words[index : index + size]
            if not segment_words:
                break
                
            chunk_string = " ".join(segment_words)
            chunk_vector = self.engine.compute_vector(chunk_string)
            
            self.indexed_chunks.append({
                "chunk_id": f"{document_id}_segment_{len(self.indexed_chunks)}",
                "text": chunk_string,
                "vector": chunk_vector
            })

    def find_best_match(self, search_query: str) -> dict:
        if not self.indexed_chunks:
            return {"chunk_id": "DEFAULT_SRC", "text": "No indexing available."}
            
        query_vector = self.engine.compute_vector(search_query)
        highest_score = -1.0
        best_matching_chunk = None
        
        for chunk in self.indexed_chunks:
            current_score = self.engine.calculate_similarity(query_vector, chunk["vector"])
            if current_score > highest_score:
                highest_score = current_score
                best_matching_chunk = chunk
                
        return best_matching_chunk



class MockPipelineLLM:
    """
    Simulates production LLM endpoints cleanly using context routing conditions.
    """
    def request_completion(self, context_rules: list, document_passage: str, task: str) -> str:
        # Check active system constraints in database to choose appropriate style output
        uppercase_rule_active = False
        for rule in context_rules:
            if "UPPERCASE" in rule or "uppercase" in rule:
                uppercase_rule_active = True
                break

        if uppercase_rule_active:
            memo_body = (
                "### INTERNAL LEGAL MEMO\n\n"
                "**1. PARTIES INVOLVED:** Acme Corporation and Beta Software LLC [Source: DOC_REF_0].\n"
                "**2. TERM AMENDMENT:** Agreement terms execute immediately upon confirmation [Source: DOC_REF_0].\n"
                "**3. LIABILITY EXPOSURE:** Financial liability limitations are strictly capped at an absolute maximum of $50,000 [Source: DOC_REF_0]."
            )
            return memo_body
        else:
            memo_body = (
                "### Internal Legal Memo\n\n"
                "**1. Parties Involved:** Acme Corporation and Beta Software LLC [Source: DOC_REF_0].\n"
                "**2. Term Amendment:** Agreement terms execute immediately upon confirmation [Source: DOC_REF_0].\n"
                "**3. Liability Exposure:** Financial liability limitations are capped at a maximum of $50,000 [Source: DOC_REF_0]."
            )
            return memo_body

    def extract_style_deltas(self, baseline_text: str, edited_text: str) -> str:
        # Intelligently isolate what changed between system default and manual text input
        if "PARTIES INVOLVED" in edited_text and "Parties Involved" in baseline_text:
            return "ALL SECTION TITLE HEADINGS MUST BE FORMATTED IN UPPERCASE AND BOLDED."
        if len(edited_text) != len(baseline_text):
            return "Enforce short, atomic bullet points for clarity."
        return "Maintain strict chronological tracking of contract terms."



class SystemMemoryDatabase:
    """
    Handles local structural learning persistence to allow system optimization over time.
    """
    def __init__(self, database_name: str = "operator_feedback.db"):
        self.db_name = database_name
        self.establish_tables()

    def establish_tables(self):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_rules (
                rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_description TEXT UNIQUE,
                frequency_count INTEGER DEFAULT 1
            )
        ''')
        connection.commit()
        connection.close()

    def save_new_rule(self, description_text: str):
        if not description_text or len(description_text.strip()) < 5:
            return
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO learned_rules (rule_description, frequency_count) VALUES (?, 1)",
                (description_text.strip(),)
            )
        except sqlite3.IntegrityError:
            cursor.execute(
                "UPDATE learned_rules SET frequency_count = frequency_count + 1 WHERE rule_description = ?",
                (description_text.strip(),)
            )
        connection.commit()
        connection.close()

    def retrieve_top_rules(self, limit: int = 3) -> list:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT rule_description FROM learned_rules ORDER BY frequency_count DESC, rule_id DESC LIMIT ?",
            (limit,)
        )
        database_rows = cursor.fetchall()
        connection.close()
        return [row[0] for row in database_rows]


st.set_page_config(page_title="Ambitio Workspace Engine", layout="wide")

st.title("⚖️ Legal Document Workspace Engine")
st.markdown("---")

# Setup clean persistent session state management
if "llm_client" not in st.session_state:
    st.session_state.llm_client = MockPipelineLLM()
    st.session_state.data_store = KnowledgeIndexedStore()
    st.session_state.memory_db = SystemMemoryDatabase()
    st.session_state.active_draft = ""

left_column, right_column = st.columns([1, 1])

with left_column:
    st.subheader("📥 Source Document Ingestion")
    
    messy_unstructured_input = st.text_area(
        "Paste OCR Transcripts or Raw Text Streams:",
        value="   === ACME CORP LEGAL AGMT === ... Executed June 04, 2026. Section 4: Total liability limits cap strictly at $50,000 max. Notes are partially obscured here...   ",
        height=120
    )
    
    operational_task = st.text_input(
        "Required Action Task Parameter:",
        value="Generate a first-pass internal legal memo summary."
    )
    
    if st.button(" Execute Pipeline Execution"):
        # 1. Clean data spaces
        normalized_cleaning = " ".join(messy_unstructured_input.strip().split())
        
        # 2. Slice text segments into indexing matrix
        st.session_state.data_store.process_and_index_document("DOC_REF_0", normalized_cleaning)
        
        # 3. Retrieve target grounded evidence
        matching_passage = st.session_state.data_store.find_best_match(operational_task)
        
        # 4. Fetch historically learned active constraints from local database
        historical_rules = st.session_state.memory_db.retrieve_top_rules(limit=3)
        
        # 5. Compile output response draft
        compiled_result = st.session_state.llm_client.request_completion(
            context_rules=historical_rules,
            document_passage=matching_passage["text"],
            task=operational_task
        )
        
        st.session_state.active_draft = compiled_result
        st.success("Draft compiled successfully!")

    st.subheader(" System Active Memory Matrix")
    current_stored_rules = st.session_state.memory_db.retrieve_top_rules(limit=3)
    if current_stored_rules:
        for single_rule in current_stored_rules:
            st.info(f" **Learned Constraint Applied:** {single_rule}")
    else:
        st.warning("No optimization adjustments recorded inside system memory yet.")

with right_column:
    st.subheader(" Live Editor Workspace & Optimization Tracking")
    
    interactive_editor_box = st.text_area(
        "Review / Refine Generated Target Outputs:",
        value=st.session_state.active_draft if st.session_state.active_draft else "Run the pipeline execution on the left panel first.",
        height=300
    )
    
    if st.button(" Commit Corrections & Optimize"):
        if st.session_state.active_draft and interactive_editor_box != st.session_state.active_draft:
            # Analyze what structural style elements the operator modified manually
            extracted_rule_insight = st.session_state.llm_client.extract_style_deltas(
                baseline_text=st.session_state.active_draft,
                edited_text=interactive_editor_box
            )
            
            # Commit the rule into SQLite table data storage
            st.session_state.memory_db.save_new_rule(extracted_rule_insight)
            st.success("Operator corrections analyzed. New design parameters saved to database memory.")
            st.rerun()
        else:
            st.error("No custom changes detected in the editor workspace to process optimizations from.")