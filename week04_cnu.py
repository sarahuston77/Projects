"""Extra practice."""

import math
import numpy as np

# def intersection():
#     """Finds coordinates of points of intersection."""
    
#     # Find roots using coefficents of new polynomial to solve i.e. intersection.
#     roots = np.roots([2, 5, math.sqrt(5) - 1])

#     # Plug into equation
#     if roots[0] < roots[1]:
#         print(f'Root 1:\n{roots[0], (roots[0] ** 2) + (3 * roots[0]) + math.sqrt(5)}\nRoot 2:\n{roots[1], (roots[1] ** 2) + (3 * roots[1]) + math.sqrt(5)}')
#     else:
#         print(f'Root 1:\n{roots[1], (roots[1] ** 2) + (3 * roots[1]) + math.sqrt(1)}\nRoot 2:\n{roots[0], (roots[0] ** 2) + (3 * roots[0]) + math.sqrt(5)}')



# import numpy as np

def vector_angles(r1: np.array(float), r2: np.array(float)) -> float and float:
    """Computes dot product and angle btwn two vectors."""
    return round(np.dot(r1, r2), 2), ((np.dot(r1, r2)) / (np.linalg.norm(r1) * np.linalg.norm(r2)))


r1 = np.array([1., 1., 0.])
r2 = np.array([0., 1., 0.])

print(vector_angles(r1, r2))