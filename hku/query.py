import re
import json
import asyncio

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed


async def initialize_rag():
    rag = LightRAG(
        working_dir="output",
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
        enable_llm_cache=False
    )

    await rag.initialize_storages()

    return rag


async def hku_query(
    user_query: str,
    mode: str = "local",
    response_type: str = "Multiple Paragraphs",
    top_k: int = 10,
    chunk_top_k: int = 5,
    enable_rerank: bool = False,
):
    rag = await initialize_rag()

    query_param_context = QueryParam(
        mode=mode,
        only_need_context=True,
        response_type=response_type,
        top_k=top_k,
        chunk_top_k=chunk_top_k,
        enable_rerank=enable_rerank
    )

    query_param = QueryParam(
        mode=mode,
        response_type=response_type,
        top_k=top_k,
        chunk_top_k=chunk_top_k,
        enable_rerank=enable_rerank
    )
    
    context = await rag.aquery(user_query, param=query_param_context)
    response = await rag.aquery(user_query, param=query_param)

    pattern = r"```json\n(.*?)\n```"
    json_blocks = re.findall(pattern, context, re.DOTALL)

    entities_str = json_blocks[0]
    relationships_str = json_blocks[1]
    entities = json.loads(entities_str)
    relationships = json.loads(relationships_str)

    return response, (entities, relationships)


if __name__ == "__main__":
    async def main():
        response, (entities, relationships) = await hku_query("What are the top themes in this story?")
        print("Entities:\n", entities)
        print("\n" + "=" * 150 + "\n")
        print("Relationships:\n", relationships)
        print("\n" + "=" * 150 + "\n")
        print("Response:\n", response)

    asyncio.run(main())


