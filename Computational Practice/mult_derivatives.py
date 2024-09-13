"""My first practice assignment."""

# list of polynomial coefficents w/ index corresponding to power
coefficent_list: list[float] = [1.0, 2.0, 4.0, 3.0]

def reverse_list(foward_list: list[float]) -> list[float]:
    """Will create a new modified list if need to reverse order of polynomial."""
    # will splice the list in a -1 stepwise fashion
    return coefficent_list[::-1]

import math

def deriv_cal(coef_list: list[float], num_deriv: int, point: int) -> int:
    """Will calculate the derivative to the num_deriv power at a specific point."""
    # create an empty list to sum each point
    new_list: list[float] = []
    # loops through the list of coefficents
    for idx in range(0, len(coef_list)):
        fact_coef: float = 1.0
        # says that if nth degree is less than num of dervivatives taken, 
        # it will skip since in this model, we are using positive degrees only
        if idx - num_deriv >= 0:
            # uses factorial formula from math to compute a piece of the coefficent
            # then multiply by given coef using index and plug in given point to this as well
            fact_coef = (math.factorial(idx))/(math.factorial(idx - num_deriv))
            new_list.append(coef_list[idx] * (fact_coef) * (point ** (idx - num_deriv)))
    # sum the total of each term and assign this value to an empty total variable
    deriv_total: float = sum(new_list)
    return deriv_total

print(deriv_cal(coefficent_list, 2, 1))
print(reverse_list(coefficent_list))

print('slay')

            # i: int = 0
            # a: int = 1
            # # used i to subtract the appropriate number from n and multiple this
            # while i < num_deriv:
            #     factorial = idx - i
            #     a *= factorial
            #     i += 1
            # new_list.append(coef_list[idx] * (a) * (point ** (idx - num_deriv)))