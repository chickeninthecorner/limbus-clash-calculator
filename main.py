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

def get_power_probabilities(skill):
    heads_probability = skill.sanity / 100 + 0.5
    tails_probability = 1 - heads_probability

    result = {}

    for head_count in range(0, skill.coin_count + 1):
        tail_count = skill.coin_count - head_count

        power = skill.base_power + skill.coin_power * head_count
        power = max(power, 0)
        probability = heads_probability ** head_count * tails_probability ** tail_count * combination(skill.coin_count, head_count)
        result[power] = probability

    return result

skill1 = NormalCoinSkill(1, 2, 1, 25)
r = get_power_probabilities(skill1)
print(r)