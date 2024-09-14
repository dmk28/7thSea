def get_initials(string):
    # Split the string into words
    words = string.split()
    # Get the first letter of each word and join them
    initials = ''.join(word[0].upper() for word in words if word)
    return initials