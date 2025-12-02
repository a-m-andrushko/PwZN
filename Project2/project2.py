import argparse
import numpy as np
from scipy.signal import convolve2d
from PIL import Image
import glob
from rich.progress import track
import time

class Ising:    

    def __init__(self, n, rho, J, B, b, S):
        self.n = int(n)
        self.rho = float(rho)
        self.J = float(J)
        self.B = float(B)
        self.b = float(b)
        self.S = int(S)

        N = self.n * self.n   # total number of spins
        N_plus = int(rho * N)   # number of +1 spins
        N_minus = N - N_plus   # number of -1 spins
        spins_init = np.array([1] * N_plus + [-1] * N_minus)
        np.random.shuffle(spins_init)   # randomise spin distribution
        self.spins = spins_init.reshape((self.n, self.n))


    def mc_step(self):
        # Step 1: Choose a random spin and calculate energy before flipping
        i = np.random.randint(0, self.n)
        j = np.random.randint(0, self.n)
        E_before = self.calc_local_energy(i, j)

        # Step 2: Flip its value and calculate energy after it
        if self.spins[i, j] == 1:
            self.spins[i, j] = -1
        else:
            self.spins[i, j] = 1
        E_after = self.calc_local_energy(i, j)

        # Step 3: Calculate energy difference
        dE = E_after - E_before

        # Step 4: Acceptance of the random spin
        if dE < 0:
            pass
        else:
            p = np.random.uniform()
            P = np.exp(-self.b * dE)
            if p < P:
                pass
            else:
                if self.spins[i, j] == 1:
                    self.spins[i, j] = -1
                else:
                    self.spins[i, j] = 1


    def calc_local_energy(self, i, j):   # calculate only local energy changes
        kernel = np.array([[0, 1, 0],   # kernel for 4 nearest neighbours
                           [1, 0, 1],
                           [0, 1, 0]])
        
        patch = self.spins.take(range(i-1, i+2), mode='wrap', axis=0)\
                          .take(range(j-1, j+2), mode='wrap', axis=1)   # periodic boundary conditions via 'wrap'

        neighbour_sum = convolve2d(patch, kernel, mode='same', boundary='wrap') # calculate local neighbour sum (convolution)
        
        E_int = -0.5 * self.J * np.sum(patch * neighbour_sum)   # interaction energy
        E_field = -self.B * np.sum(patch)   # external field energy
        return E_int + E_field
    
    
    def calc_whole_energy(self, spins, J, B):   # calculate energy changes for the whole grid
        kernel = np.array([[0, 1, 0],   # kernel for 4 nearest neighbours
                           [1, 0, 1],
                           [0, 1, 0]])
        
        neighbour_sum = convolve2d(spins, kernel, mode='same', boundary='wrap')   # periodic boundary conditions via 'wrap'
        E_int = -0.5 * J * np.sum(spins * neighbour_sum)   # interaction energy term
        E_field = -B * np.sum(spins)   # external field term
        return E_int + E_field
    
    
    def calc_magnetisation(self, n, spins):   # calculate magnetisation
        return 1 / (n * n) * np.sum(spins)


def main():
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

    model = Ising(args.size, args.rho, args.J_value, args.B_value, args.beta_value, args.steps)

    open(f'{args.magnetisation}.txt', 'w').close()   # clear the file for new magnetisation data
    open('energy.txt', 'w').close()   # clear the file for new energy data

    # Simulation loop
    start = time.time()
    for i in track(range(args.steps), description='⚛️  [bold magenta]2D Ising Simulation in progress...[/bold magenta] ⚛️  '):   # macrostepping
        for j in range(args.size * args.size):   # microstepping
            model.mc_step()

        # Save grid states each macrostep
        if not args.prefix:
            pass
        else:
            pixel_array = np.where(model.spins == 1, 255, 0).astype(np.uint8)
            img = Image.fromarray(pixel_array, mode='L')
            img.save(f'{args.prefix}{i}.png')

        # Save magnetisation data each macrostep
        if not args.magnetisation:
            pass
        else:
            with open(f'{args.magnetisation}.txt', 'a') as f:
                f.write(f'{i}\t{model.calc_magnetisation(args.size, model.spins)}\n')   # append magnetisation data

        # Save energy data each macrostep
        with open('energy.txt', 'a') as f:
            f.write(f'{i}\t{model.calc_whole_energy(model.spins, args.J_value, args.B_value)}\n')   # append energy data
    end = time.time()
    print(f'Time: {end - start} s')

    # Create animation out of saved grid states
    if not args.animation:
        pass
    else:
        frames = [Image.open(img) for img in sorted(glob.glob('image_*.png'))]   # load all saved frames and sort by index

        frames[0].save(
            f'{args.animation}.gif',
            save_all=True,
            append_images=frames[1:],  # append remaining frames
            duration=200,              # time between frames in ms
            loop=0                     # 0 = loop forever
        )


main()