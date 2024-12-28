#Code for interface

import dearpygui.dearpygui as dpg
from typing import List,Tuple
import numpy as np
import random
from SimWindow import SimWindow

#import os
#os.chdir("C:/Users/lucyr/Dropbox/PC/Documents/CompBiom/IntroPro")

def main_menu():
  """Main menu of the programme with a informal greeting message. Users can select option (1): to
generate map and cars randomly,(2): to generate the map and cars using the provided file, or (3) to quit the programme."""
  print("\nHey there! Welcome to the Map of a Flat Country Programme.")
  print("Build some maps, drop some cars, and see if everything connects smoothly.")
  print("Ready to dive in? Let's go!\n")
  
  option = input('''\nSelect one of the following: 
                 1) Generate the map randomly
                 2) Generate the map from the provided file 
                 3) Quit
                 \nPlease enter your choice: ''').strip()
  if option == "1":
    menu_random() #display the menu for random map generation
  elif option == "2": 
    menu_provided() #display the menu for map generation using a file
  elif option == "3": 
    print("\nGoodbye")
    exit(0) #quit programme
  else: 
    print("\nOption \"" + option + "\" not recognised, please enter a number that corresponds to one of the options displayed.")
    main_menu()

def menu_random():
    """Submenu of the programme. Users define the number of segments they want for the random map."""
    global segments #ensures segements are saved globally for downstream visualisation
    while True:
        segments_random = input(
            '''\nHow many segments do you want the map to have (number needs to be an even number that is greater than 2)? ''').strip()
        try:
            segs_random = int(segments_random)
            if segs_random > 2 and segs_random % 2 == 0: #input must be greater than 2 and divisible by 2
                segments = generate_random_segments(segs_random)
                print(f"\nGenerating {segs_random} segments...")

                #Use are_segements_connected() function to validate the map
                if are_segments_connected(segments):
                    print("\nGreat! Map is valid and connected.")
                    menu_cars(segments)  #Proceed to car placement menu
                else:
                    print("\nMap is not valid or connected. Please try again.")
                    continue
                break
            else:
                print("\nPlease enter an even number that is greater than 2.")
        except ValueError:
            print("\nInvalid input. Please enter a valid number.")

def generate_random_segments(num_segments):
    """
    Generate a list of interconnected road segments.
    """
    if num_segments < 2:
        raise ValueError("\nNumber of segments must be at least 2 to form a closed loop.")

    segments = []
    min_distance = 10  #Minimum distance between segments

    #Generate the starting point of the first segment
    start_x, start_y = random.randint(0, 500), random.randint(0, 500)
    x1, y1 = start_x, start_y  #generate start point

    def is_valid_new_segment(new_segment):
        """Check if the new segment has no overlaps."""
        (x1, y1), (x2, y2) = new_segment

        for (sx1, sy1), (sx2, sy2) in segments:
            #Check overlap
            if sx1 == sx2 and x1 == x2 and sx1 == x1:  #x1 = x2 if line is vertical
                if not (max(y1, y2) < min(sy1, sy2) - min_distance or min(y1, y2) > max(sy1, sy2) + min_distance):
                    return False
            elif sy1 == sy2 and y1 == y2 and sy1 == y1:  #y1 = y2 is line is horizontal
                if not (max(x1, x2) < min(sx1, sx2) - min_distance or min(x1, x2) > max(sx1, sx2) + min_distance):
                    return False

            #this was removed as it slowed down the code due to too much validation steps.
            # Check proximity
           # if sx1 == sx2 and abs(x1 - sx1) < min_distance and abs(x2 - sx1) < min_distance:  # Vertical proximity
            #    if not (max(y1, y2) < min(sy1, sy2) or min(y1, y2) > max(sy1, sy2)):
             #       return False
            #elif sy1 == sy2 and abs(y1 - sy1) < min_distance and abs(y2 - sy1) < min_distance:  # Horizontal proximity
             #   if not (max(x1, x2) < min(sx1, sx2) or min(x1, x2) > max(sx1, sx2)):
              #      return False
        return True

    #Generate initial segments
    for _ in range(num_segments - 2):  #Generate num_segments - 2 segments because we add 2 at the end to close the road
        while True:
            #Randomly decide if the segment is horizontal or vertical
            direction = random.choice([-1, 1])  #Choose positive or negative to randomise the direction of the segment
            if random.choice([True, False]):  #Horizontal segment
                x2, y2 = x1 + direction * random.randint(10, 100), y1
            else:  #Vertical segment
                x2, y2 = x1, y1 +  random.randint(10, 100)

            new_segment = ((x1, y1), (x2, y2))

            #Check if the new segment is valid
            if is_valid_new_segment(new_segment):
                segments.append(new_segment)
                x1, y1 = x2, y2  #Update current point
                break  #Exit the loop once a valid segment is added

    #Add segments 2 to close the the road
    while x1 != start_x or y1 != start_y:
        if x1 != start_x:  #Align x-coordinate
            new_segment = ((x1, y1), (start_x, y1))
            if is_valid_new_segment(new_segment):
                segments.append(new_segment)
                x1 = start_x

        if y1 != start_y:  #Align y-coordinate
            new_segment = ((x1, y1), (x1, start_y))
            if is_valid_new_segment(new_segment):
                segments.append(new_segment)
                y1 = start_y

    return segments

#Map validation: check if segments connected and not overlapping

def are_segments_connected(segments):
    """
    Checks whether the given segments are all connected, ensures no diagonal segments exist, 
    and ensures no segments overlap.

    Parameters:
        segments (list of tuples): Each segment is a tuple ((x1, y1), (x2, y2)).

    Returns:
        bool: True if all segments are connected, have no diagonal segments, and do not overlap, 
        False otherwise.
    """
    #Validate that no segment is diagonal
    for i, ((x1, y1), (x2, y2)) in enumerate(segments):
        if x1 != x2 and y1 != y2:  #Both x and y coordinates change, making the segment diagonal
            print(f"Error: Segment {i+1} is diagonal: (({x1}, {y1}), ({x2}, {y2})).")
            return False

    #Validate that no segments overlap
    for i, ((x1, y1), (x2, y2)) in enumerate(segments):
        for j, ((x3, y3), (x4, y4)) in enumerate(segments):
            if i != j:  #Avoids checking itself
                #Check if segment i overlaps segment j (collinear and within bounds)
                if x1 == x2 == x3 == x4:  #Vertical overlap
                    if max(min(y1, y2), min(y3, y4)) < min(max(y1, y2), max(y3, y4)):
                        print(f"Error: Segment {i+1} overlaps with segment {j+1}.")
                        return False
                elif y1 == y2 == y3 == y4:  #Horizontal overlap
                    if max(min(x1, x2), min(x3, x4)) < min(max(x1, x2), max(x3, x4)):
                        print(f"Error: Segment {i+1} overlaps with segment {j+1}.")
                        return False

    #Extract start and end points into separate lists
    start_points = [segment[0] for segment in segments]  # Extract (x1, y1)
    end_points = [segment[1] for segment in segments]    # Extract (x2, y2)

    #Initialize connectedness status and create a visited list.
    visited = [False] * len(segments)
    visited[0] = True  # Start with the first segment

    #Queue for next segments 
    queue = [0]

    while queue:
        current = queue.pop(0)
        current_end = end_points[current]

        for i, start in enumerate(start_points):
            if not visited[i] and current_end == start:
                visited[i] = True
                queue.append(i)

    #If not all segments are visited, return False
    if not all(visited):
        print("Error: Not all segments are connected.")
        return False

    return True


def menu_provided():
    """Submenu of the program. Users specify the file location for map creation."""
    global segments
    while True:
        option = input("\nIs the file in the same folder as this Python file (Yes or No)? ").strip().lower()

        if option == "yes":
            file_name = input("\nPlease type the full name of the file with its extension (e.g., map_data.txt): ").strip()
            if opener(file_name):  #File loaded successfully
                break
        elif option == "no":
            file_path = input("\nPlease provide the full path to the file (e.g., C:/path/to/your/file.txt): ").strip()
            if opener(file_path):  #File loaded successfully
                break
        else:
            print("\nInvalid option. Please enter 'Yes' or 'No'.")

def opener(file_path):
    """
    Opens a file, processes it to create segments, and checks connectivity to validate the segments.

    Parameters:
        file_path (str): Path to the file containing segment data.

    Returns:
        bool: True if the map is valid and connected, False otherwise.
    """
    global segments #ensures segements are saved globally for downstream visualisation
    try:
        #Read segments from the file
        segments = read_segments_from_file(file_path)

        #Validate the segments
        if len(segments) == 0:  # Use len() to check for empty list
            print("\nError: No valid segments found in the file.")
            return False

        print(f"\nLoading {len(segments)} segments from the file...")

        #Check if the segments are connected
        if are_segments_connected(segments):
            print("\nGreat! Map is valid and connected with no overlaps.")
            menu_cars(segments) #Proceed to car placement menu
            return True
        else:
            print("\nError: Map is not valid or not fully connected.")
            return False

    except FileNotFoundError:
        print(f"\nError: File not found at {file_path}. Please check the filename or path.")
    except Exception as e:
        print(f"\nUnexpected error while reading the file: {e}")
    return False



def read_segments_from_file(file_path):
    """
    Reads segment data from a file and converts them to tuples.

    Parameters:
        file_path (str): Path to the file containing segment data.

    Returns:
        list of tuples: A list of segments, each represented as ((x1, y1), (x2, y2)).
    """
    segments = []
    with open(file_path, 'r') as file:
        for line in file:
            #Strip whitespace and check if the line is valid
            line = line.strip()
            if not line or line.startswith("#"):  #Skip if line is empty or if line is a comment
                continue
            try:
                #Convert the line into floats and structure it as a tuple 
                x1, y1, x2, y2 = map(float, line.split(','))
                segments.append(((x1, y1), (x2, y2)))  #Store as tuple of tuples
            except ValueError:
                print(f"\nSkipping invalid line: {line}")
    return segments

def menu_cars(segments):
    """Submenu for generating car positions (1) randomly on the road segments,(2) through a provided file, or (3) to return to the main menu."""

    choice = input('''\nSelect one of the following:\n
                    1) Generate car positions randomly
                    2) Generate car positions from provided file
                    3) Go back to the main menu
                    \nEnter your choice: ''').strip()
    if choice == "1":
        return menu_random_cars()
    elif choice == "2":
        return menu_provided_cars(segments)
    elif choice == "3":
        print("\nReturning to the main menu.")
        return main_menu()
    else:
        print(f"\nChoice \"{choice}\" not recognized. Please try again.")
        menu_cars(segments)

def menu_random_cars():
    """Submenu of the programme. Users define the number of cars they want randomly place on the road map."""
    global cars #ensures cars is saved globally for downstream visualisation
    while True:
        cars_random = input(
            '''\nHow many cars do you want to place on the road? ''').strip()
        try:
            cars_random = int(cars_random)
            if cars_random > 0:
                cars = generate_random_cars(cars_random)
                #Validate the car positions
                if validate_car_positions(cars, segments):
                    print(f"\nGenerating {cars_random} cars...")
                    menu_simulation()  #go to menu with the option to visualise road map
                    break
                else:
                    print("\nError: Some cars are not valid. Regenerating...")
                    continue  #Regenerate cars
            else:
                print("\nPlease enter a number greater than 0.")
        except ValueError:
            print("\nInvalid input. Please enter a valid number.")
        

def generate_random_cars(num_cars):
    """
    Generate random car positions that lay on the road segments.

    Parameters:
        num_cars (int): Number of cars to generate.

    Returns:
        list of tuples: List of car positions as (x, y) coordinates.
    """
    car_positions = []  #List to store the generated car positions

    for _ in range(num_cars):
        #Randomly select a segment
        segment = random.choice(segments)
        (x1, y1), (x2, y2) = segment

        if x1 == x2:  #Vertical segment
            #Generate a random y-coordinate along the segment
            car_y = random.randint(int(min(y1, y2)), int(max(y1, y2)))
            car_x = int(x1)  #x-coordinate is fixed for vertical segments
        elif y1 == y2:  #Horizontal segment
            #Generate a random x-coordinate along the segment
            car_x = random.randint(int(min(x1, x2)), int(max(x1, x2)))
            car_y = int(y1)  #y-coordinate is fixed for horizontal segments
        else:
            raise ValueError("\nSegments must be strictly horizontal or vertical.")

        car_positions.append((car_x, car_y))

    return car_positions

def menu_provided_cars(segments):
    """Submenu for providing a file to load car positions."""
    global cars
    while True:
        option = input("\nIs the car file in the same folder as this Python file (Yes or No)? ").strip().lower()

        if option == "yes":
            file_name = input("\nPlease type the full name of the file with its extension (e.g., cars.txt): ").strip()
            if opener_car(file_name, segments):  #File loaded successfully
                break
        elif option == "no":
            file_path = input("\nPlease provide the full path to the file (e.g., C:/path/to/cars.txt): ").strip()
            if opener_car(file_path, segments):  #File loaded successfully
                break
        else:
            print("\nInvalid option. Please enter 'Yes' or 'No'.")

def opener_car(file_path, segments):
    """Opens a file, processes it to create car positions, and checks their validity."""
    global cars
    try:
        cars = read_segments_from_file_cars(file_path)
        if validate_car_positions(cars, segments):
            print("\nPlacing cars on roads...")
            menu_simulation()  #Go to menu with the option to visualise road map
            return True
        else:
            print("\nError: Some cars are not placed on valid roads.")
            return False
    except FileNotFoundError:
        print(f"\nError: File not found at {file_path}. Please check the filename or path.")
    except Exception as e:
        print(f"\nUnexpected error while reading the file: {e}")
    return False


def read_segments_from_file_cars(file_path):
    """Reads car data from a file."""
    cars = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                x, y = map(float, line.split(','))
                cars.append((x, y))  #Store cars as tuples
            except ValueError:
                print(f"\nSkipping invalid line: {line}")
    return cars

def validate_car_positions(cars, segments):
    """Validates that all cars are placed on valid road segments."""
    for car in cars:
        valid = False
        for segment in segments:
            if is_point_on_segment(car, segment):
                valid = True
                break
        if not valid:
            print(f"\nCar at position {car} is not on any valid road segment.")
            return False
    return True

def is_point_on_segment(point, segment):
    """
    Checks if a point lies on a line segment.

    Parameters:
        point (list): [x, y] coordinates of the point.
        segment (list): [x1, y1, x2, y2] coordinates of the segment.

    Returns:
        bool: True if the point lies on the segment, False otherwise.
    """
    x, y = point
    (x1, y1), (x2, y2) = segment
    
    #Check collinearity and bounds
    if not (min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2)):
        return False

    # Check collinearity using cross-product
    cross_product = (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1)
    return abs(cross_product) < 1e-9


def menu_simulation():
    """
    Final menu to congratulate the user and provide options to visualise or quit the programme.
    """
    print("\nCongratulations! You've made a valid road map and each car has been placed on the road.")
    while True:
        choice = input('''\nWhat would you like to do next?\n
        1) Visualise the road map
        2) Quit
        \nPlease enter your choice: ''').strip()

        if choice == "1":
            #Visualize the map and cars
            sim = SimWindow(segments, cars)  #SimWindow imported from Antonio file
            sim.show()
            print("\nBeautiful. Returning to main...") #Could delete
            main_menu() #Used to be break
        elif choice == "2":
            print("\nGoodbye!")
            exit(0)
        else:
            print(f"\nChoice \"{choice}\" not recognized. Please try again.")
            
if __name__ == "__main__":
  main_menu()
