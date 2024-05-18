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
