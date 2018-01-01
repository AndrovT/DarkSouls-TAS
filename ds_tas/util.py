"""
Helpful utility functions

"""

# If this grows too big we'll make it a module but for now keep it simple.


def largest_val(*vals):
    current_val = 0
    for val in vals:
        if abs(val) > abs(current_val):
            current_val = val
    return current_val
