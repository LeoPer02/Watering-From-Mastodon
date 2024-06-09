import logging


def check_pass(password):
    if password is None or password == "":
        res = {
            "error": "Password not provided"
        }
        return res
    if len(password) < 8:
        res = {
            "error": "Password length should be at least 8 characters"
        }
        return res
    return None

def check_user(username):
    if username is None:
        res = {
            "error": "Username not provided"
        }
        return res
    if len(username) < 6:
        res = {
            "error": "Username length should be at least 6 characters"
        }
        return res
    return None

def process_values(input_str):
    # Split the input string by '*'
    logging.log(logging.ERROR, f"msg: {input_str}")
    try:
        parts = input_str.split('*')
    except TypeError:
        return None, None, None, None, None
    # Check if there are exactly 5 parts
    if len(parts) != 5:
        return None, None, None, None, None

    variables = []
    for i, part in enumerate(parts):
        try:
            logging.log(logging.ERROR, f"Part[{i}] -> {part}")
            if i == 0:
                # The first variable should be an integer
                variables.append(int(part))
            else:
                # The other variables should be floats
                variables.append(float(part))
        except ValueError:
            # If conversion fails, append None
            variables.append(None)

    # Unpack the variables list into five separate variables
    var1, var2, var3, var4, var5 = variables
    return var1, var2, var3, var4, var5
