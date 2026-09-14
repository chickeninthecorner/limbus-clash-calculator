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

class NormalCoinSkill:
    def __init__(self, base_power, coin_count, coin_power, sanity):
        self.base_power = base_power
        self.coin_count = coin_count
        self.coin_power = coin_power
        self.sanity = sanity
