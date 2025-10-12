"""Generate API documentation stubs for Python packages."""
import os
from os.path import join
from pathlib import Path


def main() -> None:
    project_dir = Path(__file__).joinpath(*[".."]*2)
    docs_folder = join(".mkdocs", "docs")
    

    modules = [ # relative paths to the module src files
        "packages/data_foundation/src",
        "packages/data_science/src",
        "libs/analytics_utils/src",
        "libs/data_platform_utils/src",
    ]

    remove_old(project_dir, docs_folder)
    create_new(project_dir, docs_folder, modules)

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
    docs_paths = docs_root.glob("**/*.md")

    # delete old stubs
    for doc_path in docs_paths:
        delete_file = False
        with open(doc_path) as file:
            if file.readline().startswith("::: "):
                delete_file = True
        if delete_file:
            os.remove(doc_path)
    
    # delete empty directories
    for dirpath, dirnames, filenames in os.walk(docs_root, topdown=False):
        if not dirnames and not filenames:
            os.removedirs(dirpath)

def create_new(project_dir: Path, docs_folder: str, modules:list[str]) -> None:
    modules_rel_path = Path(join(docs_folder, "modules"))
    
    roots = [(
            Path(join(project_dir, module)).resolve(),
            Path(join(project_dir, modules_rel_path, module.split("/")[0])).resolve())
        for module in modules
    ]

    for source_root, doc_root in roots:
        # get all python source files in all sub directories
        source_paths = source_root.glob("**/*.py")
        for source_path in source_paths:

            # skip empty file
            with open(source_path) as file:
                if not "".join(file.readlines()).replace(" ",""):
                    continue

            # convert file path to import path in dot notation
            import_path = compile_path(source_root, source_path, sep=".")

            # generate the .md file path for the documentation stub
            doc_rel_path = compile_path(source_root, source_path, sep="/", suffix=".md")
            doc_path = Path(join(doc_root, doc_rel_path))

            # rename __init__ files to their parent name
            if doc_path.name == "__init__.md":
                doc_path = doc_path.with_name(doc_path.parent.name).with_suffix(".md")

            os.makedirs(doc_path.parent, exist_ok=True)
            with open (doc_path, "w") as file:
                file.write("::: " + import_path)

main()
