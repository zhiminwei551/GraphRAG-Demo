from pathlib import Path

from graphrag.cli.query import run_local_search

def msft_query(
    query: str,
    community_level: int = 2,
    response_type: str = "Multiple Paragraphs",
    config_filepath=None,
    data_dir=None,
    root_dir=Path(),
    streaming=False,
    verbose=False
):
    response, context_data = run_local_search(
        config_filepath=config_filepath,
        data_dir=data_dir,
        root_dir=root_dir,
        community_level=community_level,
        response_type=response_type,
        streaming=streaming,
        query=query,
        verbose=verbose,
    )
    return response, context_data


if __name__ == "__main__":
    response, context_data = msft_query("What is A Christmas Carol?")
    print("Response:\n", response)
    print("\nContext Data:\n", context_data)


