import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.models import Slider, Div, ColumnDataSource


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

# Initial parameters
beta0 = 0.01
gamma0 = 0.5

# Initial solution
solution = odeint(sir_model, y0, t, args=(beta0, gamma0))
S, I, R = solution.T

# Data source to store data
source = ColumnDataSource(data=dict(t=t, S=S, I=I, R=R))

# Plot
fig = figure(width=600, height=400, title="SIR Model")

line_S = fig.line('t', 'S', source=source, line_width=2, color='blue', legend_label='S')
line_I = fig.line('t', 'I', source=source, line_width=2, color='red', legend_label='I')
line_R = fig.line('t', 'R', source=source, line_width=2, color='green', legend_label='R')

circles_S = fig.circle('t', 'S', source=source, size=1, color='cyan')
circles_I = fig.circle('t', 'I', source=source, size=1, color='pink')
circles_R = fig.circle('t', 'R', source=source, size=1, color='yellow')

fig.legend.location = "right"

s_beta = Slider(title='$$\\beta$$', start=0.0005, end=0.05, value=beta0, step=0.0005, width=200)
s_gamma = Slider(title='$$\\gamma$$', start=0.05, end=1.0, value=gamma0, step=0.05, width=200)
s_width = Slider(title='Line width', start=1, end=5, value=1, step=0.5, width=200)
s_size = Slider(title='Marker size', start=0, end=5, value=1, step=0.5, width=200)

# Update parameters
def update_data(attr, old, new):
    update_beta = float(s_beta.value)
    update_gamma = float(s_gamma.value)

    solution = odeint(sir_model, y0, t, args=(update_beta, update_gamma))
    S, I, R = solution.T
    source.data = dict(t=t, S=S, I=I, R=R)

def update_width(attr, old, new):
    for l in (line_S, line_I, line_R):
        l.glyph.line_width = s_width.value

def update_size(attr, old, new):
    for c in (circles_S, circles_I, circles_R):
        c.glyph.size = s_size.value

s_beta.on_change('value', update_data)
s_gamma.on_change('value', update_data)
s_width.on_change('value', update_width)
s_size.on_change('value', update_size)

# Draw
curdoc().add_root(column(
    Div(text="<h2>SIR Model</h2>"),
    row(s_beta, s_gamma, s_width, s_size),
    fig
))