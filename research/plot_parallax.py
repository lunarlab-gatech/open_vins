#!/usr/bin/env python3
"""
Simple script to plot feature parallax over time from OpenVINS TrackKLT output.
Reads CSV files from /tmp/parallax_left.csv and /tmp/parallax_right.csv
"""

import getpass
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os

def plot_parallax(csv_path, camera_name):
    """Plot parallax statistics from a CSV file."""
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return None

    df = pd.read_csv(csv_path)

    # Convert timestamp to relative time (starting from 0)
    df['time'] = df['timestamp'] - df['timestamp'].iloc[0]

    return df

def main():
    username = getpass.getuser()
    left_path = f"/home/{username}/open_vins_ws/src/open_vins/parallax_left.csv"
    right_path = f"/home/{username}/open_vins_ws/src/open_vins/parallax_right.csv"

    # Allow custom paths via command line
    if len(sys.argv) > 1:
        left_path = sys.argv[1]
    if len(sys.argv) > 2:
        right_path = sys.argv[2]

    df_left = plot_parallax(left_path, "Left")
    df_right = plot_parallax(right_path, "Right")

    if df_left is None and df_right is None:
        print("No parallax data files found.")
        print("Run OpenVINS first to generate /tmp/parallax_left.csv and /tmp/parallax_right.csv")
        sys.exit(1)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Feature Parallax Over Time', fontsize=14)

    # Plot left camera
    if df_left is not None:
        ax1 = axes[0, 0]
        ax1.plot(df_left['time'], df_left['mean_px'], label='Mean', color='blue')
        ax1.fill_between(df_left['time'],
                         df_left['mean_px'] - df_left['std_px'],
                         df_left['mean_px'] + df_left['std_px'],
                         alpha=0.3, color='blue', label='Std Dev')
        ax1.plot(df_left['time'], df_left['median_px'], label='Median', color='orange', linestyle='--')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Parallax (pixels)')
        ax1.set_title('Left Camera - Mean/Median Parallax')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2 = axes[0, 1]
        ax2.plot(df_left['time'], df_left['min_px'], label='Min', color='green')
        ax2.plot(df_left['time'], df_left['max_px'], label='Max', color='red')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Parallax (pixels)')
        ax2.set_title('Left Camera - Min/Max Parallax')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

    # Plot right camera
    if df_right is not None:
        ax3 = axes[1, 0]
        ax3.plot(df_right['time'], df_right['mean_px'], label='Mean', color='blue')
        ax3.fill_between(df_right['time'],
                         df_right['mean_px'] - df_right['std_px'],
                         df_right['mean_px'] + df_right['std_px'],
                         alpha=0.3, color='blue', label='Std Dev')
        ax3.plot(df_right['time'], df_right['median_px'], label='Median', color='orange', linestyle='--')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Parallax (pixels)')
        ax3.set_title('Right Camera - Mean/Median Parallax')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        ax4 = axes[1, 1]
        ax4.plot(df_right['time'], df_right['min_px'], label='Min', color='green')
        ax4.plot(df_right['time'], df_right['max_px'], label='Max', color='red')
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Parallax (pixels)')
        ax4.set_title('Right Camera - Min/Max Parallax')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

    # Add number of features plot
    fig2, ax_feat = plt.subplots(figsize=(12, 4))
    if df_left is not None:
        ax_feat.plot(df_left['time'], df_left['num_features'], label='Left Camera', color='blue')
    if df_right is not None:
        ax_feat.plot(df_right['time'], df_right['num_features'], label='Right Camera', color='red')
    ax_feat.set_xlabel('Time (s)')
    ax_feat.set_ylabel('Number of Features')
    ax_feat.set_title('Number of Tracked Features Over Time')
    ax_feat.legend()
    ax_feat.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
