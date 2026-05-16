import os
import json
import re
import faiss
from dotenv import load_dotenv
from ddgs import DDGS
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient

# Load the API key from the .env file
load_dotenv()
hf_token = os.getenv("HF_API_TOKEN")
class TextVerificationPipeline:
    def __init__(self):
        print("[*] Initializing Hybrid Text Pipeline...")
        
        # 1. Load Tier 1: Semantic Cache Model (Will auto-detect and use your local GPU!)
        print("[*] Loading Local Embedding Model to CPU...")
        # device='cuda' forces it to use your newly integrated GPU for lightning-fast embeddings
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu',token=hf_token)
        self.embedding_dim = self.embedder.get_embedding_dimension()
        self.faiss_index = faiss.IndexFlatL2(self.embedding_dim)
        self.cache_metadata = [] 
        
        self._build_dummy_cache()

        # 2. Connect to Tier 2: Cloud Hosted Qwen LLM
        print("[*] Connecting to Hugging Face Cloud Inference...")
        # hf_token = os.getenv("HF_API_TOKEN")
        if not hf_token:
            raise ValueError("Missing HF_API_TOKEN in .env file!")
            
        self.hf_client = InferenceClient(api_key=hf_token)
        # We specify the exact model hosted on HF's servers
        self.cloud_model_id = "Qwen/Qwen2.5-7B-Instruct"
        
        print("[*] Pipeline Ready! Waiting for queries...\n")

    def _build_dummy_cache(self):
        """Pre-loads known fake/real news into the local FAISS index."""
        historical_data = [
            {"text": "The Earth is flat and NASA is faking space images.", "label": "Fake", "reason": "Known conspiracy theory debunked centuries ago."},
            {"text": "Water is composed of two hydrogen atoms and one oxygen atom.", "label": "Real", "reason": "Established scientific fact."}
        ]
        for item in historical_data:
            vector = self.embedder.encode([item["text"]]).astype('float32')
            self.faiss_index.add(vector)
            self.cache_metadata.append(item)

    def _tier_1_cache_search(self, query, threshold=0.6):
        """Checks local FAISS cache. Runs in microseconds on local GPU."""
        query_vector = self.embedder.encode([query]).astype('float32')
        distances, indices = self.faiss_index.search(query_vector, 1) 
        
        if distances[0][0] < threshold and indices[0][0] != -1:
            match = self.cache_metadata[indices[0][0]]
            return {
                "tier": 1,
                "label": match["label"],
                "confidence": round(1.0 - (distances[0][0] / 2), 2),
                "reason": match['reason']
            }
        return None

    def _fetch_live_context(self, query):
        """Fetches live web results via DuckDuckGo."""
        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=3):
                    results.append(f"Source: {r['title']} | Snippet: {r['body']}")
            return "\n".join(results)
        except Exception:
            return "No live search results available."

    def _tier_2_live_rag(self, query):
        """Queries the Hugging Face Cloud API instead of running the LLM locally."""
        live_context = self._fetch_live_context(query)
        
        system_prompt = """You are a strict factual verification engine. 
Cross-reference the user's claim against the LIVE WEB SEARCH RESULTS.
RULES:
1. False based on context -> "Fake"
2. True based on context -> "Real"
3. Not enough info -> "Unverified"
Output ONLY a JSON object: {"label": "Fake" | "Real" | "Unverified", "confidence": 0.0-1.0, "reason": "brief explanation"}"""

        user_prompt = f"USER CLAIM: {query}\n\nLIVE SEARCH RESULTS:\n{live_context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Call the Cloud API
        try:
            response = self.hf_client.chat_completion(
                model=self.cloud_model_id,
                messages=messages,
                max_tokens=200,
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content
            print(f"[*] Cloud Raw Output: {response_text}") #debugging line to see raw output from the cloud API
            # Safely parse the returned JSON
            json_match = re.search(r'\{.*\}', response_text.replace('\n', ''))
            result = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
            result["tier"] = 2
            return result
            
        except Exception as e:
            return {"tier": 2, "label": "Error", "reason": f"Cloud API failed: {str(e)}"}

    def verify_claim(self, query):
        print(f"[+] Analyzing: '{query}'")
        
        # 1. Local GPU Cache Check
        cache_result = self._tier_1_cache_search(query)
        if cache_result:
            print("   -> Tier 1 Cache HIT! (Local GPU)")
            return cache_result
            
        # 2. Cloud LLM Fallback
        print("   -> Tier 1 Cache MISS. Triggering Tier 2 Live RAG (Cloud API)...")
        return self._tier_2_live_rag(query)

# --- Run the Script ---
if __name__ == "__main__":
    engine = TextVerificationPipeline()
    
    while True:
        user_input = input("\nEnter a claim to verify (or type 'quit' to exit): ")
        if user_input.lower() in ['quit', 'exit']:
            break
            
        result = engine.verify_claim(user_input)
        print("\nRESULT:")
        print(json.dumps(result, indent=2))




        


# import os
# import json
# import re
# import faiss
# from dotenv import load_dotenv
# from ddgs import DDGS
# from sentence_transformers import SentenceTransformer
# from huggingface_hub import InferenceClient

# # Load the API key from the .env file
# load_dotenv()
# hf_token = os.getenv("HF_API_TOKEN")
# class TextVerificationPipeline:
#     def __init__(self):
#         print("[*] Initializing Hybrid Text Pipeline...")

#         self.weights = {
#             "historical_similarity": 15, # S
#             "source_credibility": 25,    # C
#             "web_match": 40,             # M
#             "llm_certainty": 20          # L
#         }
#         # 1. Load Tier 1: Semantic Cache Model (Will auto-detect and use your local GPU!)
#         print("[*] Loading Local Embedding Model to CPU...")

#         # device='cuda' forces it to use your newly integrated GPU for lightning-fast embeddings
#         # self.embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu',token=hf_token)
#         # self.embedding_dim = self.embedder.get_embedding_dimension()
#         # self.faiss_index = faiss.IndexFlatL2(self.embedding_dim)
#         # self.cache_metadata = [] 
        
#         self._build_dummy_cache()

#         # 2. Connect to Tier 2: Cloud Hosted Qwen LLM
#         print("[*] Connecting to Hugging Face Cloud Inference...")
#         # hf_token = os.getenv("HF_API_TOKEN")
#         if not hf_token:
#             raise ValueError("Missing HF_API_TOKEN in .env file!")
            
#         self.hf_client = InferenceClient(api_key=hf_token)
#         # We specify the exact model hosted on HF's servers
#         self.cloud_model_id = "Qwen/Qwen2.5-7B-Instruct"
        
#         print("[*] Pipeline Ready! Waiting for queries...\n")
    

#     def _calculate_weighted_score(self, s_score, c_score, m_score, l_score):
#         """Calculates the final confidence score based on predefined weights."""
#         weighted_sum = (
#             (s_score * self.weights["historical_similarity"]) +
#             (c_score * self.weights["source_credibility"]) +
#             (m_score * self.weights["web_match"]) +
#             (l_score * self.weights["llm_certainty"])
#         )
        
#         total_weight = sum(self.weights.values())
#         final_score = weighted_sum / total_weight
        
#         # Return as a clean percentage rounded to 1 decimal place
#         return round(final_score, 1)

#     def _build_dummy_cache(self):
#         """Pre-loads known fake/real news into the local FAISS index."""
#         historical_data = [
#             {"text": "The Earth is flat and NASA is faking space images.", "label": "Fake", "reason": "Known conspiracy theory debunked centuries ago."},
#             {"text": "Water is composed of two hydrogen atoms and one oxygen atom.", "label": "Real", "reason": "Established scientific fact."}
#         ]
#         for item in historical_data:
#             vector = self.embedder.encode([item["text"]]).astype('float32')
#             self.faiss_index.add(vector)
#             self.cache_metadata.append(item)

#     # def _tier_1_cache_search(self, query, threshold=0.6):
#     #     """Checks local FAISS cache. Runs in microseconds on local GPU."""
#     #     query_vector = self.embedder.encode([query]).astype('float32')
#     #     distances, indices = self.faiss_index.search(query_vector, 1) 
        
#     #     if distances[0][0] < threshold and indices[0][0] != -1:
#     #         match = self.cache_metadata[indices[0][0]]
#     #         return {
#     #             "tier": 1,
#     #             "label": match["label"],
#     #             "confidence": round(1.0 - (distances[0][0] / 2), 2),
#     #             "reason": match['reason']
#     #         }
#     #     return None

#     def _fetch_live_context(self, query):
#         """Fetches live web results via DuckDuckGo."""
#         results = []
#         try:
#             with DDGS() as ddgs:
#                 for r in ddgs.text(query, max_results=3):
#                     results.append(f"Source: {r['title']} | Snippet: {r['body']}")
#             return "\n".join(results)
#         except Exception:
#             return "No live search results available."

#     def _tier_2_live_rag(self, query):
#         live_context = self._fetch_live_context(query)
        
#         # 1. New Feature-Extraction Prompt
#         system_prompt = """You are a strict factual verification engine.
# Analyze the user's claim against the LIVE WEB SEARCH RESULTS.
# Do not calculate a final confidence score. Instead, evaluate the following variables on a scale of 0 to 100:
# - "source_credibility": Are the live search sources major news desks (80-100), unknown blogs (30-50), or missing/unrelated (0)?
# - "web_match": Does the live web actively corroborate the exact claim (80-100), omit it (0-20), or actively contradict it (0)?
# - "llm_certainty": Based on your internal knowledge and the context, how certain are you that your final label is correct (0-100)?

# RULES:
# 1. False based on context -> "Fake"
# 2. True based on context -> "Real"
# 3. Not enough info -> "Unverified"
# Output ONLY a JSON object: {"label": "Fake" | "Real" | "Unverified", "source_credibility": int, "web_match": int, "llm_certainty": int, "reason": "brief explanation"}"""

#         user_prompt = f"USER CLAIM: {query}\n\nLIVE SEARCH RESULTS:\n{live_context}"
        
#         messages = [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt}
#         ]

#         try:
#             response = self.hf_client.chat_completion(
#                 model=self.cloud_model_id,
#                 messages=messages,
#                 max_tokens=200,
#                 temperature=0.1
#             )
            
#             response_text = response.choices[0].message.content
            
#             # Parse the JSON
#             json_match = re.search(r'\{.*\}', response_text.replace('\n', ''))
#             llm_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
            
#             # 2. Programmatic Math Integration
#             # Since this is Tier 2 (a novel claim), Historical Similarity (S) is technically 0 
#             # because it missed the Tier 1 cache. 
#             final_confidence = self._calculate_weighted_score(
#                 s_score=0, 
#                 c_score=llm_data.get("source_credibility", 0),
#                 m_score=llm_data.get("web_match", 0),
#                 l_score=llm_data.get("llm_certainty", 0)
#             )

#             return {
#                 "tier": 2,
#                 "label": llm_data.get("label", "Error"),
#                 "confidence_score": f"{final_confidence}%",
#                 "breakdown": {
#                     "historical": 0,
#                     "credibility": llm_data.get("source_credibility", 0),
#                     "web_match": llm_data.get("web_match", 0),
#                     "certainty": llm_data.get("llm_certainty", 0)
#                 },
#                 "reason": llm_data.get("reason", "No reason provided.")
#             }
            
#         except Exception as e:
#             return {"tier": 2, "label": "Error", "reason": f"Pipeline failed: {str(e)}"}

#     def verify_claim(self, query):
#         print(f"[+] Analyzing: '{query}'")
        
#         # 1. Local GPU Cache Check
#         cache_result = self._tier_1_cache_search(query)
#         if cache_result:
#             print("   -> Tier 1 Cache HIT! (Local GPU)")
#             return cache_result
            
#         # 2. Cloud LLM Fallback
#         print("   -> Tier 1 Cache MISS. Triggering Tier 2 Live RAG (Cloud API)...")
#         return self._tier_2_live_rag(query)

# # --- Run the Script ---
# if __name__ == "__main__":
#     engine = TextVerificationPipeline()
    
#     while True:
#         user_input = input("\nEnter a claim to verify (or type 'quit' to exit): ")
#         if user_input.lower() in ['quit', 'exit']:
#             break
            
#         result = engine.verify_claim(user_input)
#         print("\nRESULT:")
#         print(json.dumps(result, indent=2))


