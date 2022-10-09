def typeconv(type) :
    if type == int:
        return "Intiger"
    elif type == float :
        return "Float"
    elif type == list : 
        return "Array"
    elif type == str :
        return "string"
    else :
        return f"UNHANDLED TYPE {type}"