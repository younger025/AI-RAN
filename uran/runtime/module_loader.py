from uran.ai.plan_schema import PlanSpec


def map_plan_to_module_ids(plan: PlanSpec):
    ids = []

    modulation_map = {
        "BPSK": "mod_bpsk",
        "QPSK": "mod_qpsk",
        "16QAM": "mod_16qam",
        "64QAM": "mod_64qam",
    }
    mod_id = modulation_map.get(plan.modulation)
    if mod_id:
        ids.append(mod_id)

    coding_map = {
        "repetition_2": "code_repetition_2",
        "repetition_3": "code_repetition_3",
        "convolutional_1_2": "code_conv_1_2",
        "convolutional_2_3": "code_conv_2_3",
        "ldpc_mock_2_3": "code_ldpc_mock_2_3",
        "ldpc_mock_3_4": "code_ldpc_mock_3_4",
        "ldpc_mock": "code_ldpc_mock_3_4",
    }
    code_id = coding_map.get(plan.coding_scheme)
    if code_id:
        ids.append(code_id)

    harq_map = {
        0: "harq_none",
        1: "harq_stop_and_wait",
        2: "harq_stop_and_wait",
        3: "harq_incremental_redundancy_mock",
        4: "harq_incremental_redundancy_mock",
    }
    if plan.harq_enabled and plan.harq_max_retx > 0:
        harq_id = harq_map.get(plan.harq_max_retx, "harq_stop_and_wait")
        ids.append(harq_id)

    pilot_id = f"pilot_{plan.pilot_density}"
    ids.append(pilot_id)

    scheduler_id = f"sched_{plan.scheduler}"
    ids.append(scheduler_id)

    pc_id = f"pc_{plan.power_control}"
    ids.append(pc_id)

    return ids