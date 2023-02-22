"""
Contains classes and functions that helps the main HSSM class parse arguments.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

import bambi as bmb

PriorSpec = Dict[str, Any]

PARAM_DEFAULTS = {
    "a": bmb.Prior("Uniform", lower=0.1, upper=1.0),
    "z": 0.0,
    "t": 0.0,
}


class Param:
    """
    Represents the specifications for the main HSSM class.

    Also provides convenience functions that can be used by the HSSM class to
    parse arguments.
    """

    def __init__(
        self,
        name: str,
        prior: float
        | PriorSpec
        | bmb.Prior
        | Dict[str, PriorSpec]
        | Dict[str, bmb.Prior],
        formula: str | None = None,
        link: str | bmb.Link | None = None,
    ):
        """Parses the parameters to class properties.

        Parameters
        ----------
        name
            The name of the parameter
        prior
            If a formula is not specified, this parameter expects a float value if the
            parameter is fixed or a dictionary that can be parsed by Bambi as a prior
            specification or a Bambi Prior. if a formula is specified, this parameter
            expects a dictionary of param:prior, where param is the name of the
            response variable specified in formula, and prior is either a dictionary
            that can be parsed by Bambi as a prior specification, or a Bambi Prior.
            By default None.
        formula, optional
            The regression formula if the parameter depends on other variables. The
            response variable can be omitted, by default None.
        link, optional
            The link function for the regression. It is either a string that specifies
            a built-in link function in Bambi, or a Bambi Link object. If a regression
            is speicified and link is not specified, "identity" will be used.
        """

        self.name = name
        self.formula = formula
        self.link = None

        # Check if the user has specified a formula
        self._regression = formula is not None

        if self._regression:
            if "~" not in formula:  # type: ignore
                formula = f"{self.name} ~ {formula}"

            self.formula = formula

            self.prior = {
                # Convert dict to bmb.Prior if a dict is passed
                param: (prior if isinstance(prior, bmb.Prior) else bmb.Prior(**prior))
                for param, prior in prior.items()  # type: ignore
            }

            self.link = "identity" if link is None else link
        else:
            if link is not None:
                raise ValueError("`link` should be None if no regression is specified.")

            self.prior = bmb.Prior(**prior) if isinstance(prior, dict) else prior

    def is_regression(self) -> bool:
        """Determines if a regression is specified or not.

        Returns
        -------
            A boolean that indicates if a regression is specified.
        """

        return self._regression

    def _parse_bambi(
        self,
    ) -> Tuple:
        """Returns a 3-tuple that helps with constructing the Bambi model.

        Returns
        -------
            A 3-tuple of formula, priors, and link functions that can be used to
            construct the Bambi model.
        """

        prior = {self.name: self.prior}

        if not self._regression:
            return None, prior, None

        link = {self.name: self.link}

        return self.formula, prior, link

    def __repr__(self) -> str:
        """Returns the representation of the class.

        Returns
        -------
            A string whose construction depends on whether the specification
            contains a regression or not.
        """

        if not self.is_regression():
            if isinstance(self.prior, bmb.Prior):
                return f"{self.name} ~ {self.prior}"
            return f"{self.name} = {self.prior}"

        link = (
            self.link if isinstance(self.link, str) else self.link.name  # type: ignore
        )
        priors = "\r\n".join(
            [f"{param} ~ {prior}" for param, prior in self.prior.items()]
        )

        return "\r\n".join([self.formula, f"Link: {link}", priors])  # type: ignore

    def __str__(self) -> str:
        """Returns the string representation of the class.

        Returns
        -------
            A string whose construction depends on whether the specification
            contains a regression or not.
        """
        return self.__repr__()
