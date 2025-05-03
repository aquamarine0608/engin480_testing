import numpy
import pandas
import matplotlib
import requests
import h5py
import matplotlib.pyplot as plt
import numpy as np

#Cape Wind: 41.542°N 70.321°W
#Vineyard Wind: 41°02′00″N 70°37′00″W



def parse_gwc_file(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    coordinate_line = lines[0]

    roughness_heights_sectors = list(map(int, lines[1].split()))
    n_roughness, n_heights, n_sectors = roughness_heights_sectors

    roughness_lengths = list(map(float, lines[2].split()))
    heights = list(map(float, lines[3].split()))
    
    data_start_line = 4
    lines = lines[data_start_line:]

    freq_data = np.array(list(map(float, lines[0].split())))
    
    a_params = []
    k_params = []
    for i in range(n_heights):
        a_line = list(map(float, lines[1 + 2*i].split()))
        a_params.append(a_line)
        k_line = list(map(float, lines[2 + 2*i].split()))
        k_params.append(k_line)

    a_params = np.array(a_params)
    k_params = np.array(k_params)

    result = {
        'frequencies': freq_data,
        'A_params': a_params,
        'k_params': k_params,
        'heights': heights,
        'roughness_lengths': roughness_lengths
    }
    return result

def save_as_numpy_arrays(parsed_data, output_prefix):
    np.save(f'{output_prefix}_frequencies.npy', parsed_data['frequencies'])
    np.save(f'{output_prefix}_A_params.npy', parsed_data['A_params'])
    np.save(f'{output_prefix}_k_params.npy', parsed_data['k_params'])
    np.save(f'{output_prefix}_heights.npy', np.array(parsed_data['heights']))
    np.save(f'{output_prefix}_roughness_lengths.npy', np.array(parsed_data['roughness_lengths']))

if __name__ == "__main__":
    filepath = r"C:\Users\vicda\Downloads\Vineyard Wind GWC.lib"
    parsed_data = parse_gwc_file(filepath)
    save_as_numpy_arrays(parsed_data, output_prefix='vineyard_wind')
    
class WindSite:
    def __init__(self, latitude, longitude, frequencies, a_params, k_params, heights):
        
        self.latitude = latitude
        self.longitude = longitude
        self.frequencies = frequencies
        self.a_params = a_params
        self.k_params = k_params
        self.heights = heights

    def get_distribution_at_height(self, height):
        """
        Retrieves the frequency, A, and k arrays at the specified height.
        
        Args:
            height (float): Desired height [m].

        Returns:
            tuple: (frequencies, A parameters, k parameters) for that height.
        """
        if height not in self.heights:
            raise ValueError(f"Height {height}m not available. Available heights: {self.heights}")

        idx = self.heights.index(height) if isinstance(self.heights, list) else np.where(self.heights == height)[0][0]
        a = self.a_params[idx]
        k = self.k_params[idx]
        return self.frequencies, a, k

    def summary(self):

        print(f"Wind Site at ({self.latitude}, {self.longitude})")
        print(f"Available Heights: {self.heights}")
        print(f"Number of sectors: {len(self.frequencies)}")

#data
frequencies = np.load('vineyard_wind_frequencies.npy')
a_params = np.load('vineyard_wind_A_params.npy')
k_params = np.load('vineyard_wind_k_params.npy')
heights = np.load('vineyard_wind_heights.npy')

#windsite
vineyard_site = WindSite(
    latitude=41.02,
    longitude=-70.37,
    frequencies=frequencies,
    a_params=a_params,
    k_params=k_params,
    heights=heights
)

#41°02′00″N 70°37′00″W

vineyard_site.summary()

freqs_100m, a_100m, k_100m = vineyard_site.get_distribution_at_height(100.0)

print("Frequency at 100m:", freqs_100m)
print("A parameters at 100m:", a_100m)
print("k parameters at 100m:", k_100m)

frequencies = np.load('vineyard_wind_frequencies.npy')
a_params = np.load('vineyard_wind_A_params.npy')
k_params = np.load('vineyard_wind_k_params.npy')
heights = np.load('vineyard_wind_heights.npy')

# 10 degree sectors so 36 sectors
n_sectors = len(frequencies)
sector_angles = np.linspace(0, 360, n_sectors, endpoint=False)

# ugly bar plot
plt.figure(figsize=(10,6))
plt.bar(sector_angles, frequencies, width=10, edgecolor='black', align='edge')

plt.xlabel('Wind Direction (degrees)')
plt.ylabel('Frequency (%)')
plt.title('Wind Frequency Distribution at Vineyard Wind Site')
plt.xticks(np.arange(0, 361, 30))
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

#beautiful polar plot
fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, polar=True)

theta = np.radians(sector_angles)  # Convert degrees to radians
bars = ax.bar(theta, frequencies, width=np.radians(10), edgecolor='black', align='edge')

ax.set_theta_zero_location('N')  # Set 0° to North
ax.set_theta_direction(-1)       # Clockwise

ax.set_title('Wind Frequency Wind Rose - Vineyard Wind Site', va='bottom')
plt.show()