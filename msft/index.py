import os
import shutil
from pathlib import Path

from graphrag.cli.index import index_cli
from graphrag.config.enums import IndexingMethod

def msft_index(
    root_dir=Path(),
    method=IndexingMethod.Standard.value,
    verbose=False,
    memprofile=False,
    cache=True,
    config_filepath=None,
    dry_run=False,
    skip_validation=False,
    output_dir=None,
):
    print("Deleting old files: output/*")
    shutil.rmtree("output")
    os.makedirs("output")

    index_cli(
        root_dir=root_dir,
        method=method,
        verbose=verbose,
        memprofile=memprofile,
        cache=cache,
        config_filepath=config_filepath,
        dry_run=dry_run,
        skip_validation=skip_validation,
        output_dir=output_dir,
    )


if __name__ == "__main__":
    msft_index()

