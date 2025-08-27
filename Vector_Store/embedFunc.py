\
import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle

def generate_embeddings_and_cache():
    print("embedFunc.py: Starting embedding generation and caching process...")
    # Define cache directory and file paths
    cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
    faiss_index_path = os.path.join(cache_dir, "faiss_index.idx")
    contexts_path = os.path.join(cache_dir, "product_contexts.pkl")
    
    # Initialize Sentence Transformer model
    # This model is loaded here specifically for the embedding generation process.
    # app.py will also load it for query embeddings.
    try:
        sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("embedFunc.py: SentenceTransformer model loaded successfully for embedding generation.")
    except Exception as e:
        print(f"embedFunc.py: Error loading SentenceTransformer model: {e}")
        raise  # Re-raise the exception to be caught by app.py or halt if run directly

    # --- Load and process data from CSV ---
    product_df = pd.DataFrame()
    cleaned_data_path = os.path.join(os.path.dirname(__file__), 'DataSet', 'clean_product_info.csv')
    original_data_path = os.path.join(os.path.dirname(__file__), 'DataSet', 'product_info.csv')
    data_loaded = False

    if os.path.exists(cleaned_data_path):
        try:
            product_df = pd.read_csv(cleaned_data_path)
            print(f"embedFunc.py: Successfully loaded cleaned product data from {cleaned_data_path}")
            data_loaded = True
        except Exception as e_load_clean:
            print(f"embedFunc.py: Error loading cleaned data from {cleaned_data_path}: {e_load_clean}. Trying original data.")
            product_df = pd.DataFrame() 
    
    if not data_loaded and os.path.exists(original_data_path):
        try:
            product_df = pd.read_csv(original_data_path)
            print(f"embedFunc.py: Successfully loaded original product data from {original_data_path}")
            if 'ingredients' not in product_df.columns: product_df['ingredients'] = ''
            if 'skin_type' not in product_df.columns: product_df['skin_type'] = ''
            if 'primary_category' not in product_df.columns and 'category' in product_df.columns:
                 product_df['primary_category'] = product_df['category']
            elif 'primary_category' not in product_df.columns: product_df['primary_category'] = ''
            data_loaded = True
        except Exception as e_load_orig:
            print(f"embedFunc.py: Error loading original data from {original_data_path}: {e_load_orig}")
            product_df = pd.DataFrame()

    if not data_loaded or product_df.empty:
        print("embedFunc.py: Error: No product data could be loaded. Cannot generate embeddings.")
        raise ValueError("Failed to load product data for embedding.")

    # Preprocess data columns
    product_df['product_name'] = product_df.get('product_name', pd.Series(dtype='str')).fillna('').astype(str)
    product_df['highlights'] = product_df.get('highlights', pd.Series(dtype='str')).fillna('').astype(str)
    product_df['ingredients'] = product_df.get('ingredients', pd.Series(dtype='str')).fillna('').astype(str)
    product_df['primary_category'] = product_df.get('primary_category', pd.Series(dtype='str')).fillna('').astype(str)
    product_df['skin_type'] = product_df.get('skin_type', pd.Series(dtype='str')).fillna('').astype(str)
    product_df['price_usd'] = product_df.get('price_usd', pd.Series(dtype='float')).fillna(0).astype(float)
    product_df['out_of_stock'] = product_df.get('out_of_stock', pd.Series(dtype='int')).fillna(1).astype(int)

    local_product_texts_for_embedding = []
    local_product_contexts_for_llm = []

    for index, row in product_df.iterrows():
        product_name = str(row.get('product_name', ''))
        highlights = str(row.get('highlights', ''))
        ingredients_val = str(row.get('ingredients', ''))
        category = str(row.get('primary_category', ''))
        skin_type_col_value = str(row.get('skin_type', ''))

        current_skin_types = set()
        if skin_type_col_value:
            for s_type in skin_type_col_value.split(';'):
                s_type_cleaned = s_type.strip()
                if s_type_cleaned:
                    current_skin_types.add(s_type_cleaned.capitalize())

        highlights_lower = highlights.lower()
        skin_type_map = {
            "oily skin": "Oily Skin", "dry skin": "Dry Skin",
            "combination skin": "Combination Skin", "sensitive skin": "Sensitive Skin",
            "all skin types": "All Skin Types"
        }
        for term, standardized_term in skin_type_map.items():
            if term in highlights_lower:
                already_present = any(term in existing_st.lower() for existing_st in current_skin_types)
                if not already_present:
                    current_skin_types.add(standardized_term)
        
        combined_skin_type_info = "; ".join(sorted(list(current_skin_types))) if current_skin_types else "Not specified"

        search_text = (
            f"Product Name: {product_name}. "
            f"Suitable for Skin Types: {combined_skin_type_info}. "
            f"Features and Highlights: {highlights}. "
            f"Category: {category}. "
            f"Ingredients: {ingredients_val if ingredients_val else 'Not specified'}."
        )
        local_product_texts_for_embedding.append(search_text)

        stock_info = "In Stock" if row.get('out_of_stock', 1) == 0 else "Out of Stock"
        price_usd = row.get('price_usd', 0.0)
        context_text = (
            f"Product Name: {product_name}\\n"
            f"Category: {category}\\n"
            f"Skin Type Information: {combined_skin_type_info if combined_skin_type_info != 'Not specified' else 'N/A'}\\n"
            f"Price: USD {price_usd:.2f}\\n"
            f"Stock: {stock_info}\\n"
            f"Highlights: {highlights if highlights else 'N/A'}\\n"
            f"Ingredients: {ingredients_val if ingredients_val else 'N/A'}"
        )
        local_product_contexts_for_llm.append(context_text)

    if not local_product_texts_for_embedding:
        print("embedFunc.py: No product texts generated for embedding. FAISS index cannot be built.")
        raise ValueError("No product texts generated for embedding.")

    try:
        print(f"embedFunc.py: Generating embeddings for {len(local_product_texts_for_embedding)} products...")
        embeddings = sentence_model.encode(local_product_texts_for_embedding, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')

        dimension = embeddings.shape[1]
        faiss_index_instance = faiss.IndexFlatL2(dimension)
        faiss_index_instance.add(embeddings)
        print(f"embedFunc.py: FAISS index built successfully with {faiss_index_instance.ntotal} products.")

        os.makedirs(cache_dir, exist_ok=True)
        faiss.write_index(faiss_index_instance, faiss_index_path)
        with open(contexts_path, 'wb') as f:
            pickle.dump(local_product_contexts_for_llm, f)
        print(f"embedFunc.py: Index and contexts saved to {cache_dir}")
        print("embedFunc.py: Embedding generation and caching process completed.")

    except Exception as e_build_save:
        print(f"embedFunc.py: Error building and saving FAISS index: {e_build_save}")
        raise # Re-raise to indicate failure

if __name__ == '__main__':
    # This allows running embedFunc.py directly to generate cache if needed
    print("Running embedFunc.py directly to generate cache...")
    try:
        generate_embeddings_and_cache()
        print("Cache generation successful.")
    except Exception as e:
        print(f"Cache generation failed: {e}")
