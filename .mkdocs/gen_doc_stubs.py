"""Generate API documentation stubs for Python packages."""
from os.path import join
from pathlib import Path

import mkdocs_gen_files


def replace_seperator(source_path:Path, source_root:Path, sep:str) -> str:
    return (sep
        .join(source_path
                .with_suffix("") # remove .py extension
                .parts[len(source_root.parts):] # index for relative path
        )
        .replace(".__init__", "") # remove init so parent dir name is used 
        .strip() # remove whitespace
    )

project_dir = Path(__file__).joinpath(*[".."]*2)

modules = ( # relative paths to the module src files
    "data_foundation/src",
    "data_science/src",
    "libs/analytics_utils/src",
    "libs/data_platform_utils/src",
)

roots = [(
        Path(join(project_dir, module)).resolve(),
        Path(join(project_dir, ".mkdocs", "docs", "packages", module)).resolve())
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
        import_path = replace_seperator(source_path, source_root, sep=".")

        # generate the .md file path for the documentation stub
        doc_path = join(doc_root,
                        Path(replace_seperator(source_path, source_root, sep="/")
                    ).with_suffix(".md"))
       
        
        # create mkdocs stub
        print(doc_path)
        with mkdocs_gen_files.open(doc_path, "w") as f:
            print("::: " + import_path, file=f)
