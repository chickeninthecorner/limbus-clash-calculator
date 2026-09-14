factorial_dict = {}

def factorial(x):
    if x in factorial_dict:
        return factorial_dict[x]
    if x == 0 or x == 1:
        return 1
    else:
        result = x * factorial(x - 1)
        factorial_dict[x] = result
        return result

combination_dict = {}

def combination(n, r):
    if (n, r) in combination_dict:
        return combination_dict[(n, r)]
    else:
        ans = factorial(n) / factorial(n - r) / factorial(r)
        combination_dict[(n, r)] = ans
        return ans

print(combination(4, 2))