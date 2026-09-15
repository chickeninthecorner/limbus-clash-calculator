import copy

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
    
    @property
    def id(self):
        return (self.base_power, self.coin_count, self.coin_power, self.sanity)

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

outcome_probabilities_dict = {}

def get_parry_outcome_probabilities(skill1, skill2):
    key = (skill1.id, skill2.id)
    if key in outcome_probabilities_dict:
        return outcome_probabilities_dict[key]

    power_probabilities1 = get_power_probabilities(skill1)
    power_probabilities2 = get_power_probabilities(skill2)

    result = {"win": 0.0, "tie": 0.0, "lose": 0.0}
    for power1 in power_probabilities1:
        power1_probability = power_probabilities1[power1]
        for power2 in power_probabilities2:
            power2_probability = power_probabilities2[power2]

            combined_probability = power1_probability * power2_probability
            if power1 > power2:
                result["win"] += combined_probability
            elif power1 < power2:
                result["lose"] += combined_probability
            else:
                result["tie"] += combined_probability

    outcome_probabilities_dict[key] = result
    return result

clash_dict = {}

def clash(skill1, skill2, parry):
	
	key = (skill1.id, skill2.id, parry)
	if key in clash_dict:
		return clash_dict[key]
	
	result = {"win": 0.0, "tie": 0.0, "lose": 0.0}
	if skill2.coin_count == 0:
		result["win"] = 1.0
		return result
	elif skill1.coin_count == 0:
		result["lose"] = 1.0
		return result
	elif parry == 99:
		result["tie"] = 1.0
		return result
	
	parry_outcome_probabilities = get_parry_outcome_probabilities(skill1, skill2)

	skill2_lose = copy.copy(skill2)
	skill2_lose.coin_count -= 1
	parry_win_clash_outcomes = clash(skill1, skill2_lose, parry + 1)
	skill1_lose = copy.copy(skill1) 
	skill1_lose.coin_count -= 1
	parry_lose_clash_outcomes = clash(skill1_lose, skill2, parry + 1)
	parry_tie_clash_outcomes = clash(skill1, skill2, parry + 1)
	 
	result["win"] = parry_outcome_probabilities["win"] * parry_win_clash_outcomes["win"]  + parry_outcome_probabilities["tie"] * parry_tie_clash_outcomes["win"] + parry_outcome_probabilities["lose"] * parry_lose_clash_outcomes["win"]
	result["tie"] = parry_outcome_probabilities["win"] * parry_win_clash_outcomes["tie"]  + parry_outcome_probabilities["tie"] * parry_tie_clash_outcomes["tie"] + parry_outcome_probabilities["lose"] * parry_lose_clash_outcomes["tie"]
	result["lose"] = parry_outcome_probabilities["win"] * parry_win_clash_outcomes["lose"]  + parry_outcome_probabilities["tie"] * parry_tie_clash_outcomes["lose"] + parry_outcome_probabilities["lose"] * parry_lose_clash_outcomes["lose"]
	 
	clash_dict[key] = result
	return result

skill1 = NormalCoinSkill(1, 20, 1, 0)
skill2 = NormalCoinSkill(1, 20, 1, 0)
print(clash(skill1, skill2, 0))