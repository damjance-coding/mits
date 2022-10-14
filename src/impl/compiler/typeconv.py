def typeconv(type) :
    if type == int:
        return "Intiger"
    elif type == float :
        return "Float"
    elif type == list : 
        return "Array"
    elif type == str :
        return "String"
    else :
        return f"UNHANDLED TYPE {type}"