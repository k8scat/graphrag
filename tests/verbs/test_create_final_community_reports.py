# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

from graphrag.index.workflows.v1.create_final_community_reports import (
    build_steps,
    workflow_name,
)

from .util import (
    compare_outputs,
    get_config_for_workflow,
    get_workflow_output,
    load_expected,
    load_input_tables,
    remove_disabled_steps,
)

import pandas as pd
pd.set_option('display.max_columns', None)

async def test_create_final_community_reports():
    input_tables = load_input_tables([
        "workflow:create_final_nodes",
        "workflow:create_final_covariates",
        "workflow:create_final_relationships",
    ])
    expected = load_expected(workflow_name)

    config = get_config_for_workflow(workflow_name)

    # deleting the llm config results in a default mock injection in run_graph_intelligence
    del config["create_community_reports"]["strategy"]["llm"]

    steps = remove_disabled_steps(build_steps(config))

    actual = await get_workflow_output(
        input_tables,
        {
            "steps": steps,
        },
    )

    assert len(actual.columns) == len(expected.columns)

    # only assert a couple of columns that are not mock - most of this table is LLM-generated
    compare_outputs(actual, expected, columns=["community", "level"])

    # assert a handful of mock data items to confirm they get put in the right spot
    assert actual["rank"][:1][0] == 2
    assert actual["rank_explanation"][:1][0] == "<rating_explanation>"
