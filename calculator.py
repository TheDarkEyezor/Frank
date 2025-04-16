# calculator.py

import operator

def add(x, y):
    """Return the sum of two numbers."""
    return x + y


def subtract(x, y):
    """Return the difference of two numbers."""
    return x - y


def multiply(x, y):
    """Return the product of two numbers."""
    return x * y


def divide(x, y):
    """Return the quotient of two numbers."""
    if y == 0:
        raise ValueError("Cannot divide by zero.")
    return x / y


import operator

def calculator():
    """Main function for the CLI calculator."""
    
    # Define operators
    operators = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv
    }
    
    while True:
        print("\nChoose an operation:")
        for i, (op_symbol, op_func) in enumerate(operators.items()):
            print(f"{i+1}. {op_symbol} - {op_func.__name__}")
        
        choice = input("Enter the number of your chosen operation: ")
        
        try:
            num1 = float(input("Enter the first number: "))
            num2 = float(input("Enter the second number: "))
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            continue
        
        # Convert numeric choice to operator symbol
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(operators):
                op_symbol = list(operators.keys())[choice_num - 1]
                result = operators[op_symbol](num1, num2)
                print(f"{num1} {op_symbol} {num2} = {result}")
            else:
                print("Invalid operation number. Please try again.")
        except ValueError:
            # Direct symbol input
            if choice in operators:
                try:
                    result = operators[choice](num1, num2)
                    print(f"{num1} {choice} {num2} = {result}")
                except ZeroDivisionError:
                    print("Cannot divide by zero.")
                except ValueError as e:
                    print(e)
            else:
                print("Invalid operation. Please try again.")


if __name__ == "__main__":
    calculator()