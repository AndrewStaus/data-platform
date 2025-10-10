"""Generate API documentation stubs for Python packages."""

from os.path import join
from pathlib import Path

import mkdocs_gen_files

# The package root that will be inspected for Python modules that should receive stub
# documentation pages.
src_roots = ["data_foundation/",
            #  "data_science/",
            #  "libs/"
             ]

for src_root in src_roots:
    src_root = Path(src_root)
    for path in src_root.glob("**/*.py"):
        ident = ".".join(path.with_suffix("").parts)
        ident = ident.replace(".__init__", "")

        doc_path = Path("dagster", path.relative_to(src_root)).with_suffix(".md")
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
            print("::: " + ident, file=f)