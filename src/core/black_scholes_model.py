from numpy import exp, sqrt, log
from scipy.stats import norm


class BlackScholes:
    def __init__(self, time_to_maturity: float, strike: float, current_price: float,
                 volatility: float, interest_rate: float):
        """
        Black-Scholes model for European call and put options.

        :param time_to_maturity: Time to option expiration (T).
        :param strike: Strike price (K).
        :param current_price: Current price of the underlying asset (S).
        :param volatility: Volatility of the asset (o).
        :param interest_rate: Risk-free interest rate (r).
        """
        self.time_to_maturity = time_to_maturity
        self.strike = strike
        self.current_price = current_price
        self.volatility = volatility
        self.interest_rate = interest_rate

    def black_scholes_model(self):
        """
        Computes d1 and d2 values used in the Black-Scholes formula.

        :return: Tuple (d1, d2)
        """
        T = self.time_to_maturity
        S = self.current_price
        K = self.strike
        o = self.volatility
        r = self.interest_rate

        d1 = (log(S / K) + (r + 0.5 * o ** 2) * T) / (o * sqrt(T))
        d2 = d1 - o * sqrt(T)
        return d1, d2

    def calculate_greeks(self):
        """
        Computes the Black Scholes Greeks: Delta, Gamma, Vega, Theta, and Rho.

        :return: dict
        """
        d1, d2 = self.black_scholes_model()

        T = self.time_to_maturity
        S = self.current_price
        K = self.strike
        o = self.volatility
        r = self.interest_rate

        # Delta (already computed in calculate_prices)
        call_delta = norm.cdf(d1)
        put_delta = norm.cdf(d1) - 1

        # Gamma (already computed)
        gamma = norm.pdf(d1) / (S * o * sqrt(T))

        # Vega - Sensitivity to volatility
        vega = S * norm.pdf(d1) * sqrt(T)

        # Theta - Sensitivity to time decay
        call_theta = (-S * norm.pdf(d1) * o / (2 * sqrt(T)) - r * K * exp(-r * T) * norm.cdf(d2))
        put_theta = (-S * norm.pdf(d1) * o / (2 * sqrt(T)) + r * K * exp(-r * T) * norm.cdf(-d2))

        # Rho - Sensitivity to interest rate
        call_rho = K * T * exp(-r * T) * norm.cdf(d2)
        put_rho = -K * T * exp(-r * T) * norm.cdf(-d2)

        return {
            "call_delta": call_delta,
            "put_delta": put_delta,
            "gamma": gamma,
            "vega": vega,
            "call_theta": call_theta,
            "put_theta": put_theta,
            "call_rho": call_rho,
            "put_rho": put_rho,
        }

    def calculate_prices(self):
        """
        Computes the Black-Scholes prices for call and put options.
        :return: Tuple (call_price, put_price)
        """
        d1, d2 = self.black_scholes_model()

        T = self.time_to_maturity
        S = self.current_price
        K = self.strike
        r = self.interest_rate

        call_price = S * norm.cdf(d1) - K * exp(-r * T) * norm.cdf(d2)
        put_price = K * exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

        return call_price, put_price


if __name__ == "__main__":
    time_to_maturity = 2
    strike = 90
    current_price = 100
    volatility = 0.2
    interest_rate = 0.05

    # Black Scholes
    BS = BlackScholes(
        time_to_maturity=time_to_maturity,
        strike=strike,
        current_price=current_price,
        volatility=volatility,
        interest_rate=interest_rate)
    BS.calculate_prices()
