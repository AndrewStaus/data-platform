from collections.abc import Generator
from typing import Any

import pandas as pd


def titanic() -> Generator[pd.DataFrame, Any, None]:
    from sklearn import datasets

    titanic = datasets.fetch_openml(name='titanic', version=1)

    data = pd.DataFrame(titanic["data"])
    target = pd.DataFrame(titanic["target"])
    df = pd.merge(data, target, left_index=True, right_index=True)

    yield df
