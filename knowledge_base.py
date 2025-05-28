import os
import re
import glob
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple, Optional
from utils import remove_problematic_chars # Assuming utils.py is in the same directory



def expand_query(query: str) -> str:
    """Expand query with relevant synonyms and domain-specific terms"""
    domain_specific_terms = {
        "proposal": ["offer", "bid", "solution"],
        "requirements": ["needs", "specifications", "criteria"],
        "implementation": ["deployment", "execution", "rollout"],
        "support": ["maintenance", "service", "assistance"]
    }

    words = query.split()
    expanded_words = []
    for word in words:
        expanded_words.append(word)
        for key, values in domain_specific_terms.items():
            if word.lower() == key:
                expanded_words.extend(values)
            elif word.lower() in values:
                expanded_words.append(key)

    return ' '.join(expanded_words)


class HierarchicalEmbeddingModel:
    """Model for hierarchical embeddings (document and section level)"""
    def __init__(self, model_name: str):
    # --- CHANGE HERE ---
    # Explicitly set the device. Use 'cuda' if you have a configured GPU,
    # otherwise 'cpu' is safer.
        try:
            # Try loading directly to CPU first, often resolves this.
            self.model = SentenceTransformer(model_name, device='cpu') # Modified line
            print(f"SentenceTransformer loaded on CPU for model: {model_name} (local files only)")
        except Exception as e:
            print(f"Error loading SentenceTransformer on CPU with local_files_only=True: {e}. Trying default loading.")
            # Fallback logic - if you want the fallback to *also* be local-only:
            try:
                    self.model = SentenceTransformer(model_name, local_files_only=True) # Add here too
                    print(f"SentenceTransformer loaded with local_files_only=True (default device)")
            except Exception as fallback_e:
                    print(f"Error loading SentenceTransformer even with fallback and local_files_only=True: {fallback_e}")
                    # Depending on your strictness, you might want to raise an error or handle this failure.
                    raise fallback_e # Re-raise if strictly local-only loading is mandatory

    def encode(self, texts: List[str], level: str = 'section') -> np.ndarray:
        """Generate embeddings with different pooling strategies based on level"""
        # Ensure texts are cleaned before encoding
        cleaned_texts = [remove_problematic_chars(text) for text in texts]

        if level == 'document':
            embeddings = self.model.encode(cleaned_texts, convert_to_tensor=True)
            # Use weighted pooling for document-level embeddings
            weights = np.linspace(0.1, 1.0, len(embeddings))
            weighted_embeddings = embeddings * weights[:, np.newaxis]
            return np.mean(weighted_embeddings, axis=0)
        else:
            return self.model.encode(cleaned_texts)

class ProposalKnowledgeBase:
    def __init__(self, kb_directory="markdown_responses", embedding_model="all-MiniLM-L6-v2"):
        self.kb_directory = kb_directory
        self.model = HierarchicalEmbeddingModel(embedding_model)
        self.documents = []
        self.section_map = {}
        self.metadata = []
        self.index = None
        self.tfidf_vectorizer = TfidfVectorizer()

        if not os.path.exists(kb_directory):
            os.makedirs(kb_directory)

        self.load_documents()

    def load_documents(self):
        """Load all documents from the knowledge base directory"""
        self.documents = []
        self.section_map = {}
        self.metadata = []

        if not os.path.exists(self.kb_directory):
            return

        for filename in os.listdir(self.kb_directory):
            if filename.endswith('.md') or filename.endswith('.txt'):
                file_path = os.path.join(self.kb_directory, filename)
                # Added errors='replace' here too for reading
                with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                    content = file.read()

                # Clean content immediately after reading
                cleaned_content = remove_problematic_chars(content)

                # Call the internal method using self
                sections = self._split_into_sections(cleaned_content) # Use cleaned content

                for section_name, section_content in sections.items():
                    doc_id = len(self.documents)
                    metadata = {
                        "client_industry": "general",
                        "proposal_success": True,
                        "project_size": "medium",
                        "key_differentiators": ["quality", "experience"]
                    }

                    # Apply cleaning to metadata strings if they come from filenames or external sources
                    cleaned_filename = remove_problematic_chars(filename)
                    if "_success_" in cleaned_filename:
                        metadata["proposal_success"] = cleaned_filename.split("_success_")[1].split("_")[0] == "True"
                    if "_industry_" in cleaned_filename:
                        metadata["client_industry"] = remove_problematic_chars(cleaned_filename.split("_industry_")[1].split("_")[0])
                    if "_size_" in cleaned_filename:
                        metadata["project_size"] = remove_problematic_chars(cleaned_filename.split("_size_")[1].split("_")[0])

                    self.documents.append({
                        "id": doc_id,
                        "filename": cleaned_filename, # Store cleaned filename
                        "section_name": remove_problematic_chars(section_name), # Store cleaned section name
                        "content": remove_problematic_chars(section_content), # Store cleaned content
                        "metadata": metadata
                    })

                    # Use cleaned section name for mapping
                    cleaned_section_name = remove_problematic_chars(section_name)
                    if cleaned_section_name not in self.section_map:
                        self.section_map[cleaned_section_name] = []
                    self.section_map[cleaned_section_name].append(doc_id)
                    self.metadata.append(metadata)

        self._build_index()

    # Moved this function inside the class
    def _split_into_sections(self, content):
        """Split a document into sections based on headers"""
        # Input content is assumed to be already cleaned
        sections = {}
        current_section = "Introduction"
        current_content = []

        for line in content.split('\n'):
            if line.startswith('# '):
                if current_content:
                    sections[remove_problematic_chars(current_section)] = '\n'.join(current_content)
                    current_content = []
                current_section = line[2:].strip()
            elif line.startswith('## '):
                if current_content:
                    sections[remove_problematic_chars(current_section)] = '\n'.join(current_content)
                    current_content = []
                current_section = line[3:].strip()
            else:
                current_content.append(line)

        if current_content:
            sections[remove_problematic_chars(current_section)] = '\n'.join(current_content)

        return sections

    def _build_index(self):
        """Build a FAISS index for fast similarity search"""
        if not self.documents:
            return
        # Ensure texts for indexing are cleaned
        texts = [remove_problematic_chars(doc["content"]) for doc in self.documents]
        embeddings = self.model.encode(texts)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)

    def hybrid_search(self, query, k=5):
        """Hybrid search combining dense and sparse retrieval"""
        if not self.index or not self.documents:
            return []
        # Clean the query before encoding and vectorizing
        cleaned_query = remove_problematic_chars(query)
        query_embedding = self.model.encode([cleaned_query])
        dense_scores, dense_indices = self.index.search(np.array(query_embedding).astype('float32'), k)
        query_tfidf = self.tfidf_vectorizer.transform([cleaned_query])
        sparse_scores = cosine_similarity(query_tfidf, self.tfidf_matrix).flatten()
        sparse_indices = np.argsort(-sparse_scores)[:k]
        combined = []
        seen = set()
        for idx in dense_indices[0]:
            if idx not in seen:
                combined.append((dense_scores[0][list(dense_indices[0]).index(idx)], idx))
                seen.add(idx)
        for idx in sparse_indices:
            if idx not in seen:
                combined.append((sparse_scores[idx], idx))
                seen.add(idx)
        combined.sort(key=lambda x: x[0], reverse=True)
        # Ensure document content in results is cleaned
        results = [{"score": float(score), "document": {
            "id": self.documents[idx]["id"],
            "filename": self.documents[idx]["filename"], # Already cleaned
            "section_name": self.documents[idx]["section_name"], # Already cleaned
            "content": remove_problematic_chars(self.documents[idx]["content"]), # Ensure content is cleaned
            "metadata": self.documents[idx]["metadata"] # Metadata should also be cleaned on load
        }} for score, idx in combined[:k]]
        return results

    def get_common_section_names(self, top_n=15):
        return []

    def multi_hop_search(self, initial_query, k=5):
        # Clean the initial query
        cleaned_initial_query = remove_problematic_chars(initial_query)
        first = self.hybrid_search(cleaned_initial_query, k=3*k)
        # Ensure content used for refined query is cleaned
        refined_query = cleaned_initial_query + " " + " ".join([remove_problematic_chars(r["document"]["content"])[ :200] for r in first[:3]])
        second = self.hybrid_search(refined_query, k=k)
        all_r = {r["document"]["id"]: r for r in first+second}
        topk = sorted(all_r.values(), key=lambda x: x["score"], reverse=True)[:k]
        return topk

    def get_section_documents(self, section_name):
        # Ensure section name is cleaned for lookup
        cleaned_section_name = remove_problematic_chars(section_name)
        # Ensure returned document content is cleaned
        return [{
            "id": self.documents[idx]["id"],
            "filename": self.documents[idx]["filename"],
            "section_name": self.documents[idx]["section_name"],
            "content": remove_problematic_chars(self.documents[idx]["content"]),
            "metadata": self.documents[idx]["metadata"]
        } for idx in self.section_map.get(cleaned_section_name, [])]

    def get_all_section_names(self):
        # Return cleaned section names
        return [remove_problematic_chars(name) for name in self.section_map.keys()]

    def extract_pricing_from_kb(self) -> List[int]:
        prices = []
        pattern = re.compile(r'(?:₹|Rs\.?)[\s]*([0-9,]+)')
        md_paths = glob.glob(os.path.join(self.kb_directory, '*.md'))
        for path in md_paths:
            # Added errors='replace' here too for reading
            text = open(path, 'r', encoding='utf-8', errors='replace').read()
            text = remove_problematic_chars(text) # Clean text after reading
            # Ensure regex matching is done on cleaned text
            parts = re.split(r'^#{1,3}\s*COMMERCIAL PROPOSAL\s*$', text, flags=re.IGNORECASE | re.MULTILINE)
            if len(parts) < 2:
                continue
            body = re.split(r'^#{1,3}\s+\w', parts[1], flags=re.MULTILINE)[0]
            for m in pattern.finditer(body):
                val = int(m.group(1).replace(',', ''))
                prices.append(val)
        return prices
    
   