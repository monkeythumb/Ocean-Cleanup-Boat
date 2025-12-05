import pygame
import random
import math


pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ocean Cleanup Simulation")

# Colors
DAY_COLOR = (100, 149, 237)
NIGHT_COLOR = (10, 10, 50)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
GOLD = (255, 215, 0)


DAY_DURATION_SECONDS = 12.0      
FPS = 60


METERS_PER_PIXEL = 10.0          # 10 m per pixel


BATTERY_CAPACITY_KWH = 40.0  
ENERGY_PER_KM_KWH = 0.5          
SOLAR_MAX_POWER_KW = 3.0        

#Boat
boat_pos = [WIDTH // 2, HEIGHT // 2]
boat_speed_pixels_per_sec = 80.0
sensor_range = 100
trash_radius = 8
trash_collected = 0
max_trash_capacity = 5

# Distance
distance_pixels_today = 0.0
distance_km_today = 0.0
solar_energy_kwh_today = 0.0
energy_consumed_kwh_today = 0.0
time_to_full_capacity_seconds = None  

# Battery state
battery_level_kwh = BATTERY_CAPACITY_KWH

# Time
clock = pygame.time.Clock()
time_in_day = 0.0  
current_day = 1

# Trash
num_trash = 5
trash_list = [
    [random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)]
    for _ in range(num_trash)
]

font = pygame.font.Font(None, 24)


def interpolate_color(color1, color2, factor):
    """Linearly blend between two RGB colors."""
    return tuple(int(c1 + (c2 - c1) * factor) for c1, c2 in zip(color1, color2))


def distance(p1, p2):
    """Euclidean distance between 2D points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def find_closest_trash():
    """Return the closest trash piece to the boat, if capacity not full."""
    if not trash_list or trash_collected >= max_trash_capacity:
        return None
    return min(trash_list, key=lambda t: distance(boat_pos, t))


def reset_day():
    """Reset all per-day counters (distance, energy generated, etc.)."""
    global time_in_day, distance_pixels_today, distance_km_today
    global solar_energy_kwh_today, energy_consumed_kwh_today
    global trash_collected, time_to_full_capacity_seconds, boat_pos, trash_list

    time_in_day = 0.0
    distance_pixels_today = 0.0
    distance_km_today = 0.0
    solar_energy_kwh_today = 0.0
    energy_consumed_kwh_today = 0.0
    time_to_full_capacity_seconds = None

    trash_collected = 0
    boat_pos = [WIDTH // 2, HEIGHT // 2]

    
    trash_list = [
        [random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)]
        for _ in range(num_trash)
    ]


running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # seconds since last frame
    time_in_day += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Day/Night
    day_phase = (time_in_day / DAY_DURATION_SECONDS) * math.pi * 2
    #sinusoidal factor
    time_factor = (math.sin(day_phase - math.pi / 2) + 1) / 2
    time_factor = max(0.0, min(1.0, time_factor))

    background_color = interpolate_color(NIGHT_COLOR, DAY_COLOR, time_factor)
    screen.fill(background_color)

    #Solar energy generation. 
    if time_factor > 0.05:
        power_kw = SOLAR_MAX_POWER_KW * time_factor
        delta_energy = power_kw * (dt / 3600.0)
        solar_energy_kwh_today += delta_energy
        battery_level_kwh = min(BATTERY_CAPACITY_KWH,
                                battery_level_kwh + delta_energy)

    #Boat ai & movement
    prev_boat_pos = boat_pos.copy()
    closest_trash = find_closest_trash()

    if closest_trash is not None and battery_level_kwh > 0:
        dx = closest_trash[0] - boat_pos[0]
        dy = closest_trash[1] - boat_pos[1]
        dist = math.hypot(dx, dy)

        if dist > 1:
            step = boat_speed_pixels_per_sec * dt
            boat_pos[0] += (dx / dist) * step
            boat_pos[1] += (dy / dist) * step

        # Check collection
        if distance(boat_pos, closest_trash) < 10:
            trash_list.remove(closest_trash)
            trash_collected += 1

            if trash_collected == max_trash_capacity and time_to_full_capacity_seconds is None:
                time_to_full_capacity_seconds = time_in_day

            if trash_collected < max_trash_capacity:
                trash_list.append(
                    [random.randint(50, WIDTH - 50),
                     random.randint(50, HEIGHT - 50)]
                )

    # Distance + Energy consumption
    step_pixels = distance(prev_boat_pos, boat_pos)
    distance_pixels_today += step_pixels
    distance_km_today = distance_pixels_today * METERS_PER_PIXEL / 1000.0

    # Convert distance into energy used. 
    delta_distance_km = step_pixels * METERS_PER_PIXEL / 1000.0
    delta_energy_used = delta_distance_km * ENERGY_PER_KM_KWH
    energy_consumed_kwh_today += delta_energy_used
    battery_level_kwh = max(0.0, battery_level_kwh - delta_energy_used)

    # Trash
    for trash in trash_list:
        pygame.draw.circle(screen, RED, (int(trash[0]), int(trash[1])), trash_radius)

    # Sensor range
    pygame.draw.circle(
        screen,
        WHITE,
        (int(boat_pos[0]), int(boat_pos[1])),
        sensor_range,
        1
    )
    pygame.draw.rect(
        screen,
        GRAY,
        (int(boat_pos[0]) - 20, int(boat_pos[1]) - 10, 40, 20)
    )

    # Draw: Capacity bar
    pygame.draw.rect(screen, GRAY, (50, 550, 200, 20))
    if max_trash_capacity > 0:
        filled_width = (trash_collected / max_trash_capacity) * 200
        pygame.draw.rect(screen, GREEN, (50, 550, filled_width, 20))
    screen.blit(font.render("Trash Capacity", True, WHITE), (50, 530))

    # Draw: battery bar
    battery_percent = (battery_level_kwh / BATTERY_CAPACITY_KWH) if BATTERY_CAPACITY_KWH > 0 else 0
    pygame.draw.rect(screen, GRAY, (300, 550, 200, 20))
    pygame.draw.rect(screen, GOLD, (300, 550, 200 * battery_percent, 20))
    screen.blit(font.render("Battery", True, WHITE), (300, 530))

    # Dashboard
    screen.blit(font.render(f"Day: {current_day}", True, WHITE), (20, 10))
    screen.blit(font.render(f"Trash Collected: {trash_collected}", True, WHITE), (20, 30))
    screen.blit(font.render(f"Distance: {distance_km_today:.2f} km", True, WHITE), (20, 50))
    screen.blit(font.render(f"Solar Today: {solar_energy_kwh_today:.2f} kWh", True, WHITE), (20, 70))
    screen.blit(font.render(f"Energy Used: {energy_consumed_kwh_today:.2f} kWh", True, WHITE), (20, 90))
    screen.blit(font.render(f"Battery: {battery_percent*100:.0f}% ", True, WHITE), (20, 110))

    # End of day
    if time_in_day >= DAY_DURATION_SECONDS:
        remaining_range_km = battery_level_kwh / ENERGY_PER_KM_KWH if ENERGY_PER_KM_KWH > 0 else 0
        if time_to_full_capacity_seconds is not None:
            days_to_full = time_to_full_capacity_seconds / DAY_DURATION_SECONDS
            ttf_text = f"Time to full collection: {days_to_full:.2f} days"
        else:
            ttf_text = "Time to full collection: Not reached today"

        screen.fill((0, 0, 0))
        y = HEIGHT // 2 - 80
        lines = [
            f"End of Day {current_day}",
            f"Distance travelled: {distance_km_today:.2f} km",
            f"Solar energy generated: {solar_energy_kwh_today:.2f} kWh",
            f"Energy consumed (movement): {energy_consumed_kwh_today:.2f} kWh",
            f"Battery remaining: {battery_percent*100:.1f}%",
            f"Estimated remaining range: {remaining_range_km:.1f} km",
            ttf_text,
            "Press any key to start the next day..."
        ]
        for line in lines:
            text_surf = font.render(line, True, WHITE)
            screen.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, y))
            y += 25

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    running = False
                elif event.type == pygame.KEYDOWN:
                    waiting = False

        if not running:
            break

        current_day += 1
        reset_day()

    pygame.display.flip()

pygame.quit()
