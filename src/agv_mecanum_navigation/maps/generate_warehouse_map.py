#!/usr/bin/env python3
"""Generate a warehouse occupancy grid map matching warehouse.world geometry."""
import os

# Map parameters
RESOLUTION = 0.05       # meters per pixel
WIDTH_M = 22.0          # map width in meters (slightly larger than 20m world)
HEIGHT_M = 22.0         # map height in meters
ORIGIN_X = -11.0        # map origin in world coords
ORIGIN_Y = -11.0

WIDTH_PX = int(WIDTH_M / RESOLUTION)   # 440
HEIGHT_PX = int(HEIGHT_M / RESOLUTION)  # 440

# Occupancy values
FREE = 254
OCCUPIED = 0
UNKNOWN = 205

# World geometry (from warehouse.world)
WALL_THICKNESS = 0.2
SHELF_WIDTH = 0.5
SHELF_LENGTH = 4.0

# Shelf positions (center_x, center_y)
SHELVES = [
    # Row 1 (x=-5.5)
    (-5.5, 6.0), (-5.5, 2.5), (-5.5, -6.0), (-5.5, -2.5),
    # Row 2 (x=-2.0)
    (-2.0, 6.0), (-2.0, 2.5), (-2.0, -6.0), (-2.0, -2.5),
    # Row 3 (x=+2.0)
    (2.0, 6.0), (2.0, 2.5), (2.0, -6.0), (2.0, -2.5),
    # Row 4 (x=+5.5)
    (5.5, 6.0), (5.5, 2.5), (5.5, -6.0), (5.5, -2.5),
]

def world_to_pixel(wx, wy):
    """Convert world coordinates to pixel coordinates."""
    px = int((wx - ORIGIN_X) / RESOLUTION)
    py = int((wy - ORIGIN_Y) / RESOLUTION)
    return px, py

def fill_rect(img, cx, cy, half_w, half_h):
    """Fill a rectangular obstacle centered at (cx, cy)."""
    x0, y0 = world_to_pixel(cx - half_w, cy - half_h)
    x1, y1 = world_to_pixel(cx + half_w, cy + half_h)
    x0 = max(0, min(x0, WIDTH_PX - 1))
    x1 = max(0, min(x1, WIDTH_PX - 1))
    y0 = max(0, min(y0, HEIGHT_PX - 1))
    y1 = max(0, min(y1, HEIGHT_PX - 1))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            img[y][x] = OCCUPIED

def main():
    # Initialize as free space
    img = [[FREE] * WIDTH_PX for _ in range(HEIGHT_PX)]

    # Draw walls (20x20m, centered at origin, walls at ±10m)
    ht = WALL_THICKNESS / 2.0
    # North wall (y=+10)
    fill_rect(img, 0, 10.0, 10.0 + ht, ht)
    # South wall (y=-10)
    fill_rect(img, 0, -10.0, 10.0 + ht, ht)
    # East wall (x=+10)
    fill_rect(img, 10.0, 0, ht, 10.0 + ht)
    # West wall (x=-10)
    fill_rect(img, -10.0, 0, ht, 10.0 + ht)

    # Draw shelves
    hw = SHELF_LENGTH / 2.0
    hh = SHELF_WIDTH / 2.0
    for sx, sy in SHELVES:
        fill_rect(img, sx, sy, hw, hh)

    # Write PGM file (binary format)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pgm_path = os.path.join(script_dir, 'warehouse_map.pgm')
    yaml_path = os.path.join(script_dir, 'warehouse_map.yaml')

    with open(pgm_path, 'wb') as f:
        f.write(f'P5\n{WIDTH_PX} {HEIGHT_PX}\n255\n'.encode())
        for row in img:
            f.write(bytes(row))

    # Write YAML file
    with open(yaml_path, 'w') as f:
        f.write(f'image: warehouse_map.pgm\n')
        f.write(f'resolution: {RESOLUTION}\n')
        f.write(f'origin: [{ORIGIN_X}, {ORIGIN_Y}, 0.0]\n')
        f.write(f'negate: 0\n')
        f.write(f'occupied_thresh: 0.65\n')
        f.write(f'free_thresh: 0.196\n')

    print(f'Generated: {pgm_path}')
    print(f'Generated: {yaml_path}')
    print(f'Map size: {WIDTH_PX}x{HEIGHT_PX} pixels, {WIDTH_M}x{HEIGHT_M} meters')


if __name__ == '__main__':
    main()
