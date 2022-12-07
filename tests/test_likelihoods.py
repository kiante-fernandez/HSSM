"""
Unit testing for WFPT likelihood function.

This code compares WFPT likelihood function with
old implementation of WFPT from (https://github.com/hddm-devs/hddm)
"""
import math
import os
import sys

import arviz
import numpy as np
import pymc as pm
import pytest
from hddm_wfpt import wfpt
from numpy.random import rand
from ssms.basic_simulators import simulator

sys.path.insert(0, os.path.abspath("src"))
# pylint: disable=C0413
from hssm.wfpt.classic import WFPTClassic, decision_func, log_pdf_sv


@pytest.fixture
def data_fixture():
    n_samples = 500
    sim_out = simulator(theta=[0.0, 1.5, 0.5, 1.0], model="ddm", n_samples=n_samples)
    data_tmp = sim_out["rts"] * sim_out["choices"]
    return data_tmp.flatten()


def test_kterm(data_fixture):
    """
    This function defines a range of kterms and tests results to
     makes sure they are not equal to infinity or unknown values
    """
    for k_term in range(1, 11):
        v = (rand() - 0.5) * 1.5
        sv = 0
        a = 1.5 + rand()
        z = 0.5 * rand()
        t = rand() * 0.5
        err = 1e-7
        logp = log_pdf_sv(data_fixture, v, sv, a, z, t, err, k_terms=k_term)
        logp = sum(logp.eval())
        assert not math.isinf(logp)
        assert not math.isnan(logp)


def test_decision(data_fixture):
    """
    This function tests output of decision function
    """
    decision = decision_func()
    err = 1e-7
    lambda_rt = decision(data_fixture, err)
    assert all(not v for v in lambda_rt.eval())
    assert len(data_fixture) == len(lambda_rt.eval())


def test_logp(data_fixture):
    """
    This function compares new and old implementation of logp calculation
    """
    for _ in range(20):
        v = (rand() - 0.5) * 1.5
        sv = 0
        a = 1.5 + rand()
        z = 0.5 * rand()
        t = rand() * 0.5
        err = 1e-7
        aesara_log = log_pdf_sv(data_fixture, v, sv, a, z, t, err=err)
        cython_log = wfpt.pdf_array(data_fixture, v, sv, a, z, 0, t, 0, err, 1)
        np.testing.assert_array_almost_equal(aesara_log.eval(), cython_log, 2)


def test_wfpt_class(data_fixture):
    with pm.Model():
        sv = 0
        a = 0.8
        z = 0.5
        t = 0.0

        v = pm.Normal(name="v")
        WFPTClassic(name="x", v=v, sv=sv, a=a, z=z, t=t, observed=data_fixture)
        results = pm.sample(1000, return_inferencedata=True)
        assert isinstance(results, arviz.data.inference_data.InferenceData)
