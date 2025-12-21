def flatten_list(lst):
    """Take in a list and flatten"""
    res = []
    print('calling the function')
    for item in lst:
        if isinstance(item, list): 
            res.extend(flatten_list(item))
            print('list being flattened')
        else:
            res.append(item)
    return res
print(flatten_list([1, 2, [3, 4, [1, 2]], 5, [6, 8]]))

    # Given a stack sort in ascending order
    # ex; [5, 87, 2, 34, 108, 3]
    # output - [2, 3, 5, 34, 87, 108]
    