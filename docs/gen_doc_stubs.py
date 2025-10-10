"""Generate API documentation stubs for Python packages."""

from os.path import join
from pathlib import Path

import mkdocs_gen_files

# The package root that will be inspected for Python modules that should receive stub
# documentation pages.
modules = [
    "data_foundation/data_foundation",
    "data_science/data_science",
    "libs/analytics_utils/analytics_utils",
    "libs/data_platform_utils/data_platform_utils",
]

for src_root in modules:
    src_root = Path(src_root)
    paths = src_root.glob("**/*.py")

    for path in paths:
        # do not publish docs for empty files
        with open(path, "r") as file:
            contents = file.readlines()
        if not "".join(contents).replace(" ",""):
            continue

        ident = ".".join(path.with_suffix("").parts) 
        indx = len(src_root.parts) - 1 # index for where module begins in relative path
        if ident := ".".join(path.with_suffix("").parts[indx:]).strip():
            ident = ident.replace(".__init__", "")

            doc_path = Path("data_platform", src_root, path.relative_to(src_root)).with_suffix(".md")
            if path.name == "__init__.py":
                # ``__init__`` files map to the containing package.  We collapse the generated
                # path so that the documentation renders in a sensible location within the
                # MkDocs navigation.


                doc_path = Path(
                    join(doc_path.parent, doc_path.parent.name)
                ).with_suffix(".md")

            # Emit a simple directive that instructs MkDocs to include the module level API
            # reference when documentation is built.
            with mkdocs_gen_files.open(doc_path, "w") as f:
                # print(ident)
                print("::: " + ident, file=f)