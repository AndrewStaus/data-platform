"""Generate API documentation stubs for Python packages."""
import os
import shutil
from os.path import join
from pathlib import Path


def main() -> None:
    project_dir = Path(__file__).joinpath(*[".."]*2).resolve()
    docs_folder = join(".mkdocs", "docs", "modules")
    

    packages = [ # relative paths to the module src files
        "packages/data_foundation/src",
        "packages/data_science/src",
        "libs/analytics_utils/src",
        "libs/data_platform_utils/src",
    ]

    remove_old(project_dir, docs_folder)
    process_modules(project_dir, docs_folder, packages)
    # set_index(project_dir, docs_folder)

def compile_path(source_root:Path, source_path:Path, sep:str, suffix="") -> str:
    return (sep
        .join(source_path
                .with_suffix(suffix) # remove .py extension
                .parts[len(source_root.parts):] # index for relative path
        )
        .replace(".__init__", "") # remove init so parent dir name is used 
        .strip() # remove whitespace
    )

def remove_old(project_dir, docs_folder) -> None:
    docs_root = Path(join(project_dir, docs_folder)).resolve()
    if docs_root.exists():
        shutil.rmtree(docs_root)
    os.makedirs(docs_root, exist_ok=True)
    with open(join(docs_root, ".gitkeep"), "w"):
        ...    


def process_modules(project_dir: Path, docs_folder: str, modules:list[str]) -> None:
    
    roots = [(
            Path(join(project_dir, module)).resolve(),
            Path(join(project_dir, docs_folder, module.split("/")[0])).resolve())
        for module in modules
    ]

    for source_root, doc_root in roots:
        # get all python source files in all sub directories ordered so that .md files
        # are processed first so that md documentation is applied at head of and stubs
        # are added to the end for cases where two files have the same name.
        source_paths = [
            *list(source_root.glob("**/*.md")),
            *list(source_root.glob("**/*.py"))
        ]

        for source_path in source_paths:

            # skip empty file
            with open(source_path) as file:
                if not "".join(file.readlines()).replace(" ",""):
                    continue

            # generate the .md file path for the documentation stub
            doc_rel_path = compile_path(source_root, source_path, sep="/", suffix=".md")
            doc_path = Path(join(doc_root, doc_rel_path))
            if source_path.name.lower() == "readme.md":
                doc_path = doc_path.with_name("index").with_suffix(".md")

            if source_path.suffix == ".md":
                os.makedirs(doc_path.parent, exist_ok=True)

                shutil.copyfile(source_path, doc_path)
                continue

            # convert file path to import path in dot notation
            import_path = compile_path(source_root, source_path, sep=".")

            # rename __init__ files to their parent name
            if doc_path.name == "__init__.md":
                doc_path = doc_path.with_name("index").with_suffix(".md")

            os.makedirs(doc_path.parent, exist_ok=True)
            with open(doc_path, "a") as file:
                file.write("\n::: " + import_path)

def set_index(project_dir, docs_folder) -> None:
    shutil.copyfile(
        Path(project_dir).joinpath("README.md"),
        Path(docs_folder).joinpath("index.md")
)

main()
