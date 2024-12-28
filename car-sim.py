#for car simulation 
#written for file segs1

import numpy as np
import copy
from typing import List, Optional
import unittest
from SimWindow2 import SimWindow
from geometry import Point, Segment #check these.


class Car:
    def __init__(self, position, speed, color, current_segment):
        self.position = position  # A Point object
        self.speed = speed        # A scalar for speed
        self.color = color        # A tuple (R, G, B)
        self.current_segment = current_segment  # Current road segment the car is on

    def move(self, highway_segments, cars):
        remaining_distance = self.speed
        current_position = copy.deepcopy(self.position)

        while remaining_distance > 0:
            segment_end = self.current_segment.end
            distance_to_end = np.sqrt((segment_end.x - current_position.x) ** 2 +
                                      (segment_end.y - current_position.y) ** 2)

            # Collision Avoidance
            next_car = self.get_next_car(cars)
            if next_car:
                distance_to_next_car = np.sqrt((next_car.position.x - current_position.x) ** 2 +
                                               (next_car.position.y - current_position.y) ** 2)
                if distance_to_next_car < remaining_distance:
                    self.position = Point(
                        current_position.x + (next_car.position.x - current_position.x) * 0.9,
                        current_position.y + (next_car.position.y - current_position.y) * 0.9,
                    )
                    return

            # Unobstructed Movement
            if distance_to_end > remaining_distance:
                self.position = Point(
                    current_position.x + (segment_end.x - current_position.x) * (remaining_distance / distance_to_end),
                    current_position.y + (segment_end.y - current_position.y) * (remaining_distance / distance_to_end),
                )
                return

            # Crossing Segments
            outgoing_segments = [seg for seg in highway_segments if seg.start == segment_end]
            if outgoing_segments:
                next_segment = np.random.choice(outgoing_segments)
                current_position = Point(next_segment.start.x, next_segment.start.y)
                self.current_segment = next_segment
                remaining_distance -= distance_to_end
            else:
                return

    def get_next_car(self, cars):
        """Find the next car ahead on the same segment."""
        cars_on_same_segment = [car for car in cars if car.current_segment == self.current_segment and car != self]
        cars_ahead = [car for car in cars_on_same_segment if car.position.x > self.position.x]
        return min(cars_ahead, key=lambda c: c.position.x, default=None)


class MapManager:
    def __init__(self, highway_segments, entry_gates, exit_gates, prob_injection=0.1):
        self.cars = []
        self.highway_segments = [Segment(Point(x1, y1), Point(x2, y2)) for x1, y1, x2, y2 in highway_segments]
        self.entry_gates = entry_gates  # List of Points for entry positions
        self.exit_gates = exit_gates    # List of Points for exit positions
        self.prob_injection = prob_injection

    def inject_cars(self):
        for gate in self.entry_gates:
            if np.random.rand() < self.prob_injection:
                speed = np.random.uniform(5, 15)
                color = tuple(np.random.randint(0, 256, size=3))  # Random RGB color
                current_segment = next(seg for seg in self.highway_segments if seg.start == gate)
                self.cars.append(Car(gate, speed, color, current_segment))

    def move_cars(self):
        # Use a temporary copy of the cars list to ensure consistency
        temp_cars = copy.deepcopy(self.cars)
        for car in temp_cars:
            car.move(self.highway_segments, temp_cars)

        # Update original car positions after all movements
        self.cars = temp_cars

    def remove_cars(self):
        self.cars = [car for car in self.cars if car.position not in self.exit_gates]

    def update_simulation_step(self):
        """Performs one step of the simulation."""
        self.inject_cars()
        self.move_cars()
        self.remove_cars()

        # Prepare data for updatecar
        car_positions = [(int(car.position.x), int(car.position.y)) for car in self.cars]
        car_colors = [car.color for car in self.cars]

        # Call the updatecar method from SimWindow
        SimWindow.updatecar(car_positions, car_colors)


class TrafficSimulation:
    def __init__(self, highway_segments, entry_gates, exit_gates, prob_injection=0.1):
        self.map_manager = MapManager(highway_segments, entry_gates, exit_gates, prob_injection)
        self.sim_window = SimWindow()

    def draw(self):
        self.sim_window.clear()
        for segment in self.map_manager.highway_segments:
            self.sim_window.draw_line(segment.start.x, segment.start.y, segment.end.x, segment.end.y)
        self.sim_window.refresh()

    def run(self, steps=100):
        for _ in range(steps):
            self.map_manager.update_simulation_step()
            self.draw()


# Unit Testing
class TestTrafficSimulation(unittest.TestCase):
    def test_car_injection(self):
        highway_segments = [(0, 0, 25, 0)]
        entry_gates = [Point(0, 0)]
        exit_gates = [Point(25, 0)]
        manager = MapManager(highway_segments, entry_gates, exit_gates, prob_injection=1.0)
        manager.inject_cars()
        self.assertEqual(len(manager.cars), 1)
        self.assertEqual(manager.cars[0].position, Point(0, 0))

    def test_car_movement_unobstructed(self):
        highway_segments = [(0, 0, 25, 0)]
        entry_gates = [Point(0, 0)]
        exit_gates = [Point(25, 0)]
        manager = MapManager(highway_segments, entry_gates, exit_gates)
        car = Car(Point(0, 0), 10, (255, 0, 0), manager.highway_segments[0])
        manager.cars.append(car)
        manager.move_cars()
        self.assertEqual(car.position, Point(10, 0))

    def test_car_collision_avoidance(self):
        highway_segments = [(0, 0, 25, 0)]
        entry_gates = [Point(0, 0)]
        exit_gates = [Point(25, 0)]
        manager = MapManager(highway_segments, entry_gates, exit_gates)
        car1 = Car(Point(0, 0), 10, (255, 0, 0), manager.highway_segments[0])
        car2 = Car(Point(15, 0), 5, (0, 255, 0), manager.highway_segments[0])
        manager.cars.extend([car1, car2])
        manager.move_cars()
        self.assertLess(car1.position.x, car2.position.x)


if __name__ == "__main__":
    unittest.main()
