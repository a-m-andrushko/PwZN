import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# beta -- transmission rate, probability of infection per contact × number of contacts per person per unit time
# gamma -- recovery rate, fraction of infectious individuals recovering per unit time

# SIR model differential equations
def sir_model(y, t, beta, gamma):
    S, I, R = y
    dSdt = -beta * S * I
    dIdt = beta * S * I - gamma * I
    dRdt = gamma * I
    return [dSdt, dIdt, dRdt]

# Time grid
t = np.linspace(0, 50, 500)

# Initial conditions
S0 = 100
I0 = 5
R0 = 0
y0 = [S0, I0, R0]

# Parameters
beta = 0.01
gamma = 0.5

# Solve the system
solution = odeint(sir_model, y0, t, args=(beta, gamma))
S, I, R = solution.T

# Plot
plt.plot(t, S, label='Susceptible')
plt.plot(t, I, label='Infected')
plt.plot(t, R, label='Recovered')
plt.title(r'$\beta = 0.01$, $\gamma = 0.5$ -- supercriticality')
plt.xlabel('Time')
plt.ylabel('Population')
plt.legend()
plt.grid(ls='--')
plt.tight_layout()
#plt.savefig('SIR_supercriticality.pdf')
plt.show()