import os
import sys
import asyncio

import hashlib
import colorsys
import pandas as pd
import networkx as nx
import importlib.util

class MockSignal:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

def list_files(mode):
    input_dir = f"{mode}/input"

    return [file for file in os.listdir(input_dir)]


def save_uploaded_file(uploaded_file, mode):
    input_dir = f"{mode}/input"
    file_path = os.path.join(input_dir, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path


def delete_file(filename, mode):
    file_path = os.path.join(f"{mode}/input", filename)

    os.remove(file_path)
    return True


def process_files(mode):
    original_cwd = os.getcwd()
    original_signal = sys.modules.get("signal")
    sys.modules["signal"] = MockSignal()
    os.chdir(os.path.join(original_cwd, mode))
    
    try:
        spec = importlib.util.spec_from_file_location("index", "index.py")
        index_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(index_module)

        if mode == "hku":
            asyncio.run(index_module.hku_index())
        else:
            try:
                index_module.msft_index()
            except SystemExit:
                pass
        
    except Exception as e:
        print(f"Error executing {mode}/index.py: {e}")
    finally:
        if original_signal is not None:
            sys.modules["signal"] = original_signal
        else:
            del sys.modules["signal"]
        
        os.chdir(original_cwd)


async def query_hku(user_query, mode="local", response_type="Multiple Paragraphs", top_k=10, chunk_top_k=5):
    original_cwd = os.getcwd()
    os.chdir(os.path.join(original_cwd, "hku"))
    
    try:
        spec = importlib.util.spec_from_file_location("query", "query.py")
        query_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(query_module)
        
        response, (entities, relationships) = await query_module.hku_query(
            user_query, 
            mode=mode, 
            response_type=response_type,
            top_k=top_k,
            chunk_top_k=chunk_top_k
        )
        return response, (entities, relationships)
    finally:
        os.chdir(original_cwd)


def query_msft(user_query, community_level=2, response_type="Multiple Paragraphs"):
    original_cwd = os.getcwd()
    os.chdir(os.path.join(original_cwd, "msft"))
    
    try:
        spec = importlib.util.spec_from_file_location("query", "query.py")
        query_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(query_module)
        
        response, context_data = query_module.msft_query(
            user_query,
            community_level=community_level,
            response_type=response_type
        )
        return response, context_data
    finally:
        os.chdir(original_cwd)


def get_color_from_string(text: str):
    hash_object = hashlib.md5(text.encode())
    hash_hex = hash_object.hexdigest()
    
    hash_int = int(hash_hex[:8], 16)
    h = (hash_int / 0xFFFFFFFF)
    
    s = 0.8
    v = 0.9
    
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def load_hku_full_graph():
    graph_path = "hku/output/graph_chunk_entity_relation.graphml"
    
    try:
        G = nx.read_graphml(graph_path)
        
        nodes = []
        for node_id, node_data in G.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": node_data.get("entity_id"),
                "color": get_color_from_string(node_data.get("entity_type")),
                "title": node_data.get("description")
            })
        
        edges = []
        for source, target, edge_data in G.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "title": edge_data.get("description")
            })
        
        return nodes, edges
    except Exception as e:
        print(f"Error loading HKU graph: {e}")
        return None, None


def load_msft_full_graph():
    entities_path = "msft/output/entities.parquet"
    relations_path = "msft/output/relationships.parquet"
    
    try:
        entities_df = pd.read_parquet(entities_path)
        nodes = []
        for _, row in entities_df.iterrows():
            nodes.append({
                "id": row.get("title"),
                "label": row.get("title"),
                "color": get_color_from_string(row.get("type")),
                "title": row.get("description")
            })
        
        relations_df = pd.read_parquet(relations_path)
        edges = []
        for _, row in relations_df.iterrows():
            edges.append({
                "source": row.get("source"),
                "target": row.get("target"),
                "title": row.get("description")
            })
        
        return nodes, edges
    except Exception as e:
        print(f"Error loading MSFT graph: {e}")
        return None, None


def extract_hku_subgraph(entities, relationships):
    try:
        nodes = []
        
        for entity in entities:
            entity_id = entity.get("entity")
            nodes.append({
                "id": entity_id,
                "label": entity_id,
                "color": get_color_from_string(entity.get("type")),
                "title": entity.get("description")
            })
        
        edges = []
        for rel in relationships:
            source = rel.get("entity1")
            target = rel.get("entity2")
            
            edges.append({
                "source": source,
                "target": target,
                "title": rel.get("description")
            })

        return nodes, edges
    except Exception as e:
        print(f"Error extracting HKU subgraph: {e}")
        return None, None


def extract_msft_subgraph(context_data):
    try:
        entities_df = context_data.get('entities')
        nodes = []
        
        for _, row in entities_df.iterrows():
            entity_id = row.get("entity")
            nodes.append({
                "id": entity_id,
                "label": entity_id,
                "color": get_color_from_string(entity_id),
                "title": row.get("description")
            })
        
        edges = []
        relationships_df = context_data.get('relationships')
        
        for _, row in relationships_df.iterrows():
            source = row.get("source")
            target = row.get("target")
                
            edges.append({
                "source": source,
                "target": target,
                "title": row.get("description")
                })
            
        return nodes, edges
    except Exception as e:
        print(f"Error extracting MSFT subgraph: {e}")
        return None, None

