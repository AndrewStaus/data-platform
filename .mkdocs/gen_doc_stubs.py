"""Generate API documentation stubs for Python packages."""
from os.path import join
from pathlib import Path

import mkdocs_gen_files

project_dir = Path(__file__).joinpath(*[".."] * 2)
# relative paths to the module src files
modules = (
    "data_foundation/data_foundation",
    "data_science/data_science",
    "libs/analytics_utils/analytics_utils",
    "libs/data_platform_utils/data_platform_utils",
)

roots = [(
        Path(join(project_dir, module)).resolve(),
        Path(join(project_dir, ".mkdocs", "docs", "data_platform", module)).resolve())
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
        import_path = ("."
            .join(source_path
                  .with_suffix("") # remove .py extension
                  .parts[len(source_root.parts)-1:] # index for relative path
            )
            .replace(".__init__", "") # remove init so parent dir name is used 
            .strip() # remove whitespace
        )

        # generate the .md file path for the documentation stub
        doc_path = Path(join(doc_root, source_path.relative_to(source_root)))
        # if the file is a an init file, then take the name of the parent folder
        doc_path = Path(
            join(doc_path.parent, doc_path.parent.name)
        ) if source_path.name == "__init__.py" else doc_path
        doc_path = doc_path.with_suffix(".md")        
        
        # create mkdocs stub
        with mkdocs_gen_files.open(doc_path, "w") as f:
            print("::: " + import_path, file=f)
