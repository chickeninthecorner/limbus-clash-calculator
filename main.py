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
        self.id = (base_power, coin_count, coin_power, sanity)

power_probabilities_dict = {}

def get_power_probabilities(skill):
    if skill.id in power_probabilities_dict:
        return power_probabilities_dict[skill.id]

    heads_probability = skill.sanity / 100 + 0.5
    tails_probability = 1 - heads_probability

    result = {}

    for head_count in range(0, skill.coin_count + 1):
        tail_count = skill.coin_count - head_count

        power = skill.base_power + skill.coin_power * head_count
        power = max(power, 0)
        probability = heads_probability ** head_count * tails_probability ** tail_count * combination(skill.coin_count, head_count)
        result[power] = probability

    power_probabilities_dict[skill.id] = result
    return result

winner_probabilities_dict = {}

def get_winner_probabilities(skill1, skill2):
    key = (skill1.id, skill2.id)
    if key in winner_probabilities_dict:
        return winner_probabilities_dict[key]

    power_probabilities1 = get_power_probabilities(skill1)
    power_probabilities2 = get_power_probabilities(skill2)

    win_probability = 0
    tie_probability = 0
    lose_probability = 0
    for power1 in power_probabilities1:
        power1_probability = power_probabilities1[power1]
        for power2 in power_probabilities2:
            power2_probability = power_probabilities2[power2]

            combined_probability = power1_probability * power2_probability
            if power1 > power2:
                win_probability += combined_probability
            elif power1 < power2:
                lose_probability += combined_probability
            else:
                tie_probability += combined_probability


    result = win_probability, tie_probability, lose_probability
    winner_probabilities_dict[key] = result
    return result

skill1 = NormalCoinSkill(1, 2, 1, 25)
skill2 = NormalCoinSkill(1, 2, 1, 0)

print(get_winner_probabilities(skill1, skill2))
print('test')