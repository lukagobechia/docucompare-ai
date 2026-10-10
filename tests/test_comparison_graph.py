
from docucompare.services.comparison_graph import (
    route_after_verification,
)


def test_verification_passed_ends_workflow():
    state = {
        "verification_passed": True,
        "verification_attempts": 1,
    }

    assert route_after_verification(state) == "passed"


def test_first_verification_failure_retries():
    state = {
        "verification_passed": False,
        "verification_attempts": 1,
    }

    assert route_after_verification(state) == "retry"


def test_second_verification_failure_ends_workflow():
    state = {
        "verification_passed": False,
        "verification_attempts": 2,
    }

    assert route_after_verification(state) == "failed"
