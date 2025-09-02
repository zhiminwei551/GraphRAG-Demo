import os
import asyncio

from lightrag import LightRAG
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed


async def initialize_rag():
    rag = LightRAG(
        working_dir="output",
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


async def hku_index():
    files_delete = [
        "graph_chunk_entity_relation.graphml",
        "kv_store_doc_status.json",
        "kv_store_full_docs.json",
        "kv_store_full_entities.json",
        "kv_store_full_relations.json",
        "kv_store_text_chunks.json",
        "vdb_chunks.json",
        "vdb_entities.json",
        "vdb_relationships.json",
    ]

    for file in files_delete:
        file_path = os.path.join("output", file)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleting old file: {file_path}")

    rag = await initialize_rag()

    files_input = os.listdir("input")

    for file in files_input:
        file_path = os.path.join("input", file)

        with open(file_path, "r", encoding="utf-8") as f:
            await rag.ainsert(f.read())
    
    await rag.finalize_storages()


if __name__ == "__main__":
    asyncio.run(hku_index())

