import argparse
import numpy as np
from PIL import Image
import glob
from rich.progress import track
import numba
import time

parser = argparse.ArgumentParser(description='This is a script for a 2D Ising grid')
parser.add_argument('-s', '--size', help='Size n of the Ising n x n grid', type=int)
parser.add_argument('-r', '--rho', help='Density of spins', type=float, default=0.5)
parser.add_argument('-J', '--J_value', help='Exchange coupling', type=float)
parser.add_argument('-B', '--B_value', help='External magnetic field', type=float)
parser.add_argument('-b', '--beta_value', help='Temperature -- beta = 1 / (k_B T)', type=float)
parser.add_argument('-S', '--steps', help='Number of simulation steps', type=int)
parser.add_argument('-p', '--prefix', help='Pillow images prefix', type=str)
parser.add_argument('-a', '--animation', help='Pillow animation filename', type=str)
parser.add_argument('-m', '--magnetisation', help='Filename with magnetisation data', type=str)
args = parser.parse_args()

# Initialise the Ising grid
@numba.njit
def spins(n, rho):
    N = n * n   # total number of spins
    N_plus = int(rho * N)   # number of +1 spins
    N_minus = N - N_plus   # number of -1 spins
    spins_init = np.array([1] * N_plus + [-1] * N_minus)
    np.random.shuffle(spins_init)   # randomise spin distribution
    spins = spins_init.reshape((n, n))
    return spins

@numba.njit
def mc_step(n, spins, J, B, b):
    # Step 1: Choose a random spin and calculate energy before flipping
    i = np.random.randint(0, n)
    j = np.random.randint(0, n)
    E_before = calc_local_energy(i, j, n, spins, J, B)

    # Step 2: Flip its value and calculate energy after it
    if spins[i, j] == 1:
        spins[i, j] = -1
    else:
        spins[i, j] = 1
    E_after = calc_local_energy(i, j, n, spins, J, B)

    # Step 3: Calculate energy difference
    dE = E_after - E_before

    # Step 4: Acceptance of the random spin
    if dE < 0:
        pass
    else:
        p = np.random.uniform()
        P = np.exp(-b * dE)
        if p < P:
            pass
        else:
            if spins[i, j] == 1:
                spins[i, j] = -1
            else:
                spins[i, j] = 1

# Calculate energy for MC microstepping
@numba.njit
def calc_local_energy(i, j, n, spins, J, B):   # calculate only local energy changes
    up    = spins[(i-1) % n, j]   # % n creates boundary conditions
    down  = spins[(i+1) % n, j]
    left  = spins[i, (j-1) % n]
    right = spins[i, (j+1) % n]
        
    E_int = -J * spins[i, j] * (up + down + left + right)   # interaction energy
    E_field = -B * spins[i, j]   # external field energy
    return E_int + E_field

@numba.njit
def calc_whole_energy(n, spins, J, B):   # calculate energy changes for the whole grid
    E_int = 0
    E_field = 0

    for i in range(n):
        for j in range(n):
            right = spins[i, (j+1) % n]
            down  = spins[(i+1) % n, j]

            E_int += -J * spins[i, j] * (right + down)   # interaction energy term
            E_field += -B * spins[i, j]   # external field term
    return E_int + E_field
    
@numba.njit 
def calc_magnetisation(n, spins):
    return 1 / (n * n) * np.sum(spins)


spins = spins(args.size, args.rho)

open(f"{args.magnetisation}.txt", "w").close()   # clear the file for new magnetisation data
open("energy.txt", "w").close()   # clear the file for new energy data

# Simulation loop
start = time.time()
for i in track(range(args.steps), description='⚛️  [bold magenta]2D Ising Simulation in progress...[/bold magenta] ⚛️  '):   # macrostepping
    for j in range(args.size * args.size):   # microstepping
        mc_step(args.size, spins, args.J_value, args.B_value, args.beta_value)

    # Save grid states each macrostep
    if not args.prefix:
        pass
    else:
        pixel_array = np.where(spins == 1, 255, 0).astype(np.uint8)
        img = Image.fromarray(pixel_array, mode="L")
        img.save(f"{args.prefix}{i}.png")

    # Save magnetisation data each macrostep
    if not args.magnetisation:
        pass
    else:
        with open(f"{args.magnetisation}.txt", "a") as f:
            f.write(f"{i}\t{calc_magnetisation(args.size, spins)}\n")   # append magnetisation data

    # Save energy data each macrostep
    with open("energy.txt", "a") as f:
        f.write(f"{i}\t{calc_whole_energy(args.size, spins, args.J_value, args.B_value)}\n")   # append energy data
end = time.time()
print(f'Time: {end - start} s')

# Create animation out of saved grid states
if not args.animation:
    pass
else:
    frames = [Image.open(img) for img in sorted(glob.glob("image_*.png"))]   # load all saved frames and sort by index

    frames[0].save(
        f"{args.animation}.gif",
        save_all=True,
        append_images=frames[1:],  # append remaining frames
        duration=200,              # time between frames in ms
        loop=0                     # 0 = loop forever
    )