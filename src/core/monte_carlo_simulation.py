import numpy as np
import pandas as pd


class MonteCarloSimulation:
    def __init__(self, data, forward_period, num_simulations):
        """
        Initializes the Monte Carlo Simulation.

        :param data: Historical data in the form of a pandas DataFrame.
        :param forward_period: Number of periods to simulate into the future.
        :param num_simulations: Number of simulations to run.
        """
        self.data = data
        self.forward_period = forward_period
        self.num_simulations = num_simulations
        self.simulation_results = None

    def simulate(self):
        """
        Runs the Monte Carlo simulation to generate future outcomes.
        """
        # Initialize a DataFrame to store simulation results
        simulation_outcomes = np.zeros((self.num_simulations, self.forward_period))

        # Generate random outcomes based on the historical data
        for i in range(self.num_simulations):
            # Sample from the historical data and simulate forward
            random_walk = np.random.choice(self.data.values.flatten(), size=self.forward_period)
            simulation_outcomes[i, :] = random_walk

        # Convert the results to a DataFrame
        self.simulation_results = pd.DataFrame(simulation_outcomes,
                                               columns=[f'Simulation{i + 1}' for i in range(self.forward_period)])

    def get_simulation_results(self):
        """
        Returns the results of the simulation as a DataFrame.
        """
        if self.simulation_results is None:
            raise ValueError("Simulation has not been run yet. Call simulate() first.")
        return self.simulation_results

    def get_mean_outcome(self):
        """
        Returns the mean outcome across all simulations for each period as a DataFrame.
        """
        if self.simulation_results is None:
            raise ValueError("Simulation has not been run yet. Call simulate() first.")
        mean_outcome = self.simulation_results.mean(axis=0)
        return mean_outcome

    def get_percentile_outcome(self, percentile=50):
        """
        Returns the percentile outcome (default 50th percentile) across all simulations for each period as a DataFrame.

        :param percentile: The percentile to return (default is 50th percentile, i.e., median).
        """
        if self.simulation_results is None:
            raise ValueError("Simulation has not been run yet. Call simulate() first.")
        percentile_outcome = self.simulation_results.quantile(q=percentile / 100, axis=0)
        return percentile_outcome