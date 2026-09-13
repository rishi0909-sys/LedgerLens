import torch
from transformers import AutoTokenizer, AutoModel
import imagehash
from PIL import Image
import numpy as np

class DocumentEmbedder:
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
    def get_text_embedding(self, text: str) -> np.ndarray:
        if not text.strip():
            # Return zero vector if text is empty
            return np.zeros(self.model.config.hidden_size, dtype=np.float32)
            
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        # Use mean pooling
        attention_mask = inputs['attention_mask']
        token_embeddings = outputs.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        embedding = (sum_embeddings / sum_mask).squeeze().cpu().numpy()
        
        return embedding

def get_image_hash(image_path: str) -> str:
    img = Image.open(image_path)
    # Using perceptual hash
    hash_val = imagehash.phash(img)
    return str(hash_val)

def compare_hashes(hash1: str, hash2: str) -> int:
    # Returns hamming distance
    return imagehash.hex_to_hash(hash1) - imagehash.hex_to_hash(hash2)
