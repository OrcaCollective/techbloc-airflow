from pathlib import Path

import pytest
from airflow.models import DagBag
from deployments.deployment_dags import SERVICES as DEPLOY_SERVICES


# The path to DAGs *within the container*, though that should mirror the current
# directory structure.
DAG_FOLDER = Path(__file__).parents[2] / "techbloc_airflow" / "dags"

# DAG paths to test
DAG_PATHS = [
    "deployments/deployment_dags.py",
]

# Expected count from the DagBag once a file has been parsed
# (this will likely not need to be edited for new providers)
EXPECTED_COUNT = {
    "deployments/deployment_dags.py": len(DEPLOY_SERVICES),
}


def test_dag_import_errors():
    # Attempt to load all DAGs in the DAG_FOLDER, and detect import errors
    dagbag = DagBag(dag_folder=DAG_FOLDER, include_examples=False)

    dag_errors = [Path(filename).name for filename in dagbag.import_errors]
    error_string = ",".join(dag_errors)

    assert (
        len(dagbag.import_errors) == 0
    ), f"Errors found during DAG import for files: {error_string}"


# relative_path represents the path from the DAG folder to the file
@pytest.mark.parametrize("relative_path", DAG_PATHS)
def test_dags_loads_correct_number_with_no_errors(relative_path, tmpdir):
    # For each configured DAG file, test that the expected number of DAGs
    # is loaded. Assume only 1 DAG is expected unless otherwise provided
    expected_count = EXPECTED_COUNT.get(relative_path, 1)
    dag_bag = DagBag(dag_folder=tmpdir, include_examples=False)
    dag_bag.process_file(str(DAG_FOLDER / relative_path))
    assert len(dag_bag.import_errors) == 0, "Errors found during DAG import"
    assert len(dag_bag.dags) == expected_count, "An unexpected # of DAGs was found"
