from hssm.wfpt.config import default_model_config


def test_model_paths():
    """Ensures all default model onnx files exist in the correct path."""
    for _, config in default_model_config.items():

        if config["loglik_kind"] == "approx_differentiable":
            assert config["loglik_path"].exists()
