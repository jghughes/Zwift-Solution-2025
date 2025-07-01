import numpy as np


def test_current_highest_speed_drop_paceline_solution():
    # Mock RiderContributionItem
    class MockContribution:
        def __init__(self, p1_duration, intensity_factor=1.0):
            self.p1_duration = p1_duration
            self.intensity_factor = intensity_factor

    # Mock PacelineComputationReportItem
    class MockSolution:
        def __init__(self, speed, p1_durations):
            self.calculated_average_speed_of_paceline_kph = speed
            # Simulate dict of contributions
            self.rider_contributions = {i: MockContribution(d) for i, d in enumerate(p1_durations)}
            self.compute_iterations_performed_count = 1

    # Test cases
    solutions = [
        MockSolution(40.0, [0.0, 0.0, 0.0]),  # All zero: should NOT qualify
        MockSolution(41.0, [10.0, 10.0, 10.0]),  # All nonzero: should NOT qualify
        MockSolution(42.0, [0.0, 10.0, 10.0]),  # One zero, others nonzero: should qualify
        MockSolution(43.0, [0.0, 0.0, 10.0]),  # At least one zero, at least one nonzero: should qualify (and is fastest)
    ]

    current_highest_speed_drop = float('-inf')
    current_highest_speed_drop_paceline_solution = None

    for sol in solutions:
        speed = sol.calculated_average_speed_of_paceline_kph
        contributions = sol.rider_contributions.values()
        if (
            speed > current_highest_speed_drop
            and any(c.p1_duration == 0.0 for c in contributions)
            and any(c.p1_duration != 0.0 for c in contributions)
        ):
            current_highest_speed_drop = speed
            current_highest_speed_drop_paceline_solution = sol

    assert current_highest_speed_drop_paceline_solution is not None, "No qualifying solution found"
    assert current_highest_speed_drop_paceline_solution.calculated_average_speed_of_paceline_kph == 43.0, "Incorrect solution selected"
    print("Test passed: current_highest_speed_drop_paceline_solution identified correctly.")

# Run the test
test_current_highest_speed_drop_paceline_solution()
