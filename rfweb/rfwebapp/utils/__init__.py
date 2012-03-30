from robot_htmlutils import html_escape

def normalize(string):
    return string.lower().replace(' ', '')

def eq(str1, str2):
    return normalize(str1) == normalize(str2)

def eq_any(string, strings):
    string = normalize(string)
    for s in strings:
        if normalize(s) == string:
            return True
    return False
