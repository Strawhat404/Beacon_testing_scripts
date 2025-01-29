import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json

class BeaconDataVisualizer:
    def __init__(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.rssi_data = []
        self.timestamps = []

    def animate(self, i):
        try:
            # Read the latest data
            df = pd.read_csv('beacon_data.csv')
            
            # Clear previous plots
            self.ax1.clear()
            self.ax2.clear()
            
            # Plot RSSI over time
            self.ax1.plot(df['timestamp'], df['rss
                                              , 'b-')
            self.ax1.set_title('RSSI Over Time')
            self.ax1.set_xlabel('Time')
            self.ax1.set_ylabel('RSSI (dBm)')
            plt.xticks(rotation=45)
            
            # Plot sensor data (customize based on your sensor data)
            if 'sensor_data' in df.columns:
                sensor_data = df['sensor_data'].apply(json.loads)
                # Add your sensor data plotting logic here
                
            plt.tight_layout()
            
        except Exception as e:
            print(f"Error updating plot: {str(e)}")

    def start(self):
        ani = FuncAnimation(self.fig, self.animate, interval=1000)
        plt.show()

if __name__ == "__main__":
    visualizer = BeaconDataVisualizer()
    visualizer.start()