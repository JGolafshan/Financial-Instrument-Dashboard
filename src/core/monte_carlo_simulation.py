import numpy as np
import pandas as pd
from scipy.stats import norm


class MonteCarloSimulation:
    def __init__(self, data, forward_period, backward_period, num_simulations):
        """
        Initializes the Monte Carlo Simulation.

        :param data: Historical price data as a pandas Series with datetime index.
        :param forward_period: Number of periods to simulate into the future.
        :param backward_period: Number of historical periods to include.
        :param num_simulations: Number of simulations to run.
        """
        if isinstance(data, pd.Series):
            if not isinstance(data.index, pd.DatetimeIndex):
                raise ValueError("Data must have a DatetimeIndex.")
            self.original_index = data.index
            self.start_date = data.index[-1]
            self.data = data[-backward_period:].to_numpy()
            self.historical_index = data.index[-backward_period:]
        else:
            raise TypeError("Data must be a pandas Series with a DatetimeIndex.")

        if len(self.data) < backward_period:
            raise ValueError("Not enough data for the specified backward period.")

        self.forward_period = forward_period
        self.backward_period = backward_period
        self.num_simulations = num_simulations
        self.simulation_results = None

    def simulate(self):
        """
        Runs the Monte Carlo simulation and returns price paths with historical look-back.
        """
        log_returns = np.log(self.data[1:] / self.data[:-1])
        mean = np.mean(log_returns)
        variance = np.var(log_returns)
        drift = mean - (0.5 * variance)
        daily_volatility = np.std(log_returns)

        total_periods = self.backward_period + self.forward_period
        price_paths = np.full((total_periods, self.num_simulations + 1), np.nan)

        # Fill historical data only in the first column
        price_paths[:self.backward_period, 0] = self.data

        # Simulate future paths
        current_prices = self.data[-1] * np.ones(self.num_simulations)
        for t in range(self.forward_period):
            shocks = norm.ppf(np.random.rand(self.num_simulations))
            returns = drift + daily_volatility * shocks
            current_prices *= np.exp(returns)
            price_paths[self.backward_period + t, 1:] = current_prices

        hist_dates = self.historical_index
        next_business_day = pd.bdate_range(start=hist_dates[-1] + pd.Timedelta(days=1), periods=1)[0]
        future_dates = pd.bdate_range(start=next_business_day, periods=self.forward_period)

        full_index = hist_dates.append(future_dates)

        # Column names: "Historical Data", "Simulation 1", ...
        columns = ["Historical Data"] + [f"Simulation {i}" for i in range(1, self.num_simulations + 1)]

        self.simulation_results = pd.DataFrame(price_paths, index=full_index, columns=columns)

        return self.simulation_results

    def get_simulation_results(self):
        """
        Returns the results of the simulation as a DataFrame.
        """
        if self.simulation_results is None:
            raise ValueError("Simulation has not been run yet. Call simulate() first.")
        return self.simulation_results
