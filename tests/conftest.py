import pytest

import numpy as np
import pandas as pd
import ssms

import hssm


@pytest.fixture(scope="module")
def data_ddm():
    v_true, a_true, z_true, t_true = [0.5, 1.5, 0.5, 0.5]
    obs_ddm = ssms.basic_simulators.simulator(
        [v_true, a_true, z_true, t_true], model="ddm", n_samples=100
    )
    obs_ddm = np.column_stack([obs_ddm["rts"][:, 0], obs_ddm["choices"][:, 0]])
    data = pd.DataFrame(obs_ddm, columns=["rt", "response"])

    return data


@pytest.fixture(scope="module")
def data_angle():
    v_true, a_true, z_true, t_true, theta_true = [0.5, 1.5, 0.5, 0.5, 0.3]
    obs_angle = ssms.basic_simulators.simulator(
        [v_true, a_true, z_true, t_true, theta_true], model="angle", n_samples=100
    )
    obs_angle = np.column_stack([obs_angle["rts"][:, 0], obs_angle["choices"][:, 0]])
    data = pd.DataFrame(obs_angle, columns=["rt", "response"])
    return data


@pytest.fixture(scope="module")
def data_ddm_reg():
    # Generate some fake simulation data
    intercept = 0.3
    x = np.random.uniform(0.5, 0.7, size=1000)
    y = np.random.uniform(0.4, 0.1, size=1000)

    v = intercept + 0.8 * x + 0.3 * y
    true_values = np.column_stack(
        [v, np.repeat([[1.5, 0.5, 0.5]], axis=0, repeats=1000)]
    )

    dataset_reg_v = hssm.simulate_data(
        model="ddm",
        theta=true_values,
        size=1,  # Generate one data point for each of the 1000 set of true values
    )

    dataset_reg_v["x"] = x
    dataset_reg_v["y"] = y

    return dataset_reg_v
