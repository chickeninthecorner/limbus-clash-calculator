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


class Skill:
	def __init__(
		self, base_power, coins, coin_power, sanity=0, paralysis=0
	):
		self._base_power = base_power
		self._coins = coins
		self._coin_count = len(coins)
		self._coin_power = coin_power
		self._sanity = sanity
		self._paralysis = paralysis

	@property
	def base_power(self):
		return self._base_power

	@property
	def coins(self):
		return self._coins
	
	@property
	def coin_count(self):
		return self._coin_count

	@property
	def coin_power(self):
		return self._coin_power

	@property
	def sanity(self):
		return self._sanity

	@property
	def paralysis(self):
		return self._paralysis

	@property
	def reducible(self):
		if self.base_power > 0 and self.coin_power > 0:
			return True
		if self.paralysis > 0:
			return True
		if 'S' in self.coins:
			return True
		return False

	@property
	def static_id(self):
		return (self.base_power, self.coins, self.coin_power, self.sanity)

	@property
	def dynamic_id(self):
		return (
			self.base_power,
			self.coins,
			self.coin_power, 
			self.sanity,
			self.paralysis,
		)

	@property
	def effective_rolling_id(self):
		effective_rolling_coins = []
		for coin in self.coins:
			if coin == 'C':
				effective_rolling_coins.append('C')
			else:
				effective_rolling_coins.append('N')
		effective_rolling_coins = tuple(effective_rolling_coins)

		return (
			self.base_power,
			effective_rolling_coins,
			self.coin_power,
			self.sanity,
			min(self.paralysis, self.coin_count),
		)

	@property
	def lose_skill(self):
		coins_after_losing = list(self.coins)

		broken = False
		for i in range(self.coin_count - 1, 0, -1):
			if coins_after_losing[i] == 'N':
				coins_after_losing.pop(i)
				broken = True
				break
			if coins_after_losing[i] == 'R':
				coins_after_losing[i] = 'C'
				broken = True
				break

		if broken:
			coins_after_losing = tuple(coins_after_losing)
		else:
			coins_after_losing = tuple()

		return Skill(self.base_power,
					coins_after_losing,
					self.coin_power,
					self.sanity,
					max(self.paralysis - self.coin_count, 0))

	@property
	def next_skill(self):
		return Skill(self.base_power,
					self.coins,
					self.coin_power,
					self.sanity,
					max(self.paralysis - self.coin_count, 0))

	def __str__(self):
		coins_str = ""
		for coin in self.coins:
			coins_str += coin
		return f"{self.base_power} + {self.coin_power} x {coins_str} at {self.sanity} SP and {self.paralysis} paralysis"


def get_reduced_rolling_components(skill):
	paralysis = skill.paralysis
	last_effective_coin_power = None

	result = []
	result.append(Skill(skill.base_power, ('N',), 0))
	consecutive_coins = 0

	for coin in skill.coins:
		if paralysis > 0:
			effective_coin_power = 0
		elif coin == 'C':
			effective_coin_power = skill.coin_power // abs(skill.coin_power)
		else:
			effective_coin_power = skill.coin_power

		if last_effective_coin_power is None:
			last_effective_coin_power = effective_coin_power
			consecutive_coins = 1
		elif last_effective_coin_power == effective_coin_power:
			consecutive_coins += 1
		else:
			result.append(Skill(0, ('N',) * consecutive_coins, last_effective_coin_power, skill.sanity))

			consecutive_coins = 1
			last_effective_coin_power = effective_coin_power

		paralysis = max(paralysis - 1, 0)

	result.append(Skill(0, ('N',) * consecutive_coins, last_effective_coin_power, skill.sanity))

	return result


combined_power_probabilities_dict = {}


def get_combined_power_probabilities(
	power_probabilities1, power_probabilities2
):
	key = (frozenset(power_probabilities1.items()), frozenset(power_probabilities2.items()))
	if key in combined_power_probabilities_dict:
		return combined_power_probabilities_dict[key]

	result = {}

	for power1 in power_probabilities1:
		for power2 in power_probabilities2:
			combined_power = power1 + power2
			combined_probability = (
				power_probabilities1[power1] * power_probabilities2[power2]
			)
			if combined_power not in result:
				result[combined_power] = 0.0

			result[combined_power] += combined_probability

	combined_power_probabilities_dict[key] = result
	return result


power_probabilities_dict = {}


def get_power_probabilities(skill):
	if skill.effective_rolling_id in power_probabilities_dict:
		return power_probabilities_dict[skill.effective_rolling_id]
	elif skill.reducible:
		divided_skills = get_reduced_rolling_components(skill)
		
		power_probabilities = []
		for skill in divided_skills:
			power_probabilities.append(get_power_probabilities(skill))

		combined_power_probabilities = power_probabilities[0]
		for i in range(1, len(power_probabilities)):
			combined_power_probabilities = get_combined_power_probabilities(combined_power_probabilities, power_probabilities[i])

		return combined_power_probabilities

	heads_probability = skill.sanity / 100 + 0.5
	tails_probability = 1 - heads_probability

	result = {}

	for head_count in range(0, skill.coin_count + 1):
		tail_count = skill.coin_count - head_count

		power = skill.base_power + skill.coin_power * head_count
		power = max(power, 0)
		probability = (
			heads_probability**head_count
			* tails_probability**tail_count
			* combination(skill.coin_count, head_count)
		)
		if power not in result:
			result[power] = 0.0

		result[power] += probability

	power_probabilities_dict[skill.effective_rolling_id] = result
	return result


outcome_probabilities_dict = {}


def get_parry_outcome_probabilities(skill1, skill2):
	effective_dynamic_key = (skill1.effective_rolling_id, skill2.effective_rolling_id)
	if effective_dynamic_key in outcome_probabilities_dict:
		return outcome_probabilities_dict[effective_dynamic_key]

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

	outcome_probabilities_dict[effective_dynamic_key] = result
	return result


clash_dict = {}


def clash(skill1, skill2, parry):
	dynamic_key = (skill1.dynamic_id, skill2.dynamic_id, parry)
	if dynamic_key in clash_dict:
		return clash_dict[dynamic_key]

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

	parry_outcome_probabilities = get_parry_outcome_probabilities(
		skill1, skill2
	)

	if parry_outcome_probabilities["win"] == 0.0:
		parry_win_clash_outcomes = {"win": 0.0, "tie": 0.0, "lose": 0.0}
	else:
		parry_win_clash_outcomes = clash(skill1.next_skill, skill2.lose_skill, parry + 1)

	if parry_outcome_probabilities["lose"] == 0.0:
		parry_lose_clash_outcomes = {"win": 0.0, "tie": 0.0, "lose": 0.0}
	else:
		parry_lose_clash_outcomes = clash(skill1.lose_skill, skill2.next_skill, parry + 1)

	if parry_outcome_probabilities["tie"] == 0.0:
		parry_tie_clash_outcomes = {"win": 0.0, "tie": 0.0, "lose": 0.0}
	else:
		parry_tie_clash_outcomes = clash(skill1.next_skill, skill2.next_skill, parry + 1)

	
	result["win"] = (
		parry_outcome_probabilities["win"] * parry_win_clash_outcomes["win"]
		+ parry_outcome_probabilities["tie"] * parry_tie_clash_outcomes["win"]
		+ parry_outcome_probabilities["lose"]
		* parry_lose_clash_outcomes["win"]
	)
	result["tie"] = (
		parry_outcome_probabilities["win"] * parry_win_clash_outcomes["tie"]
		+ parry_outcome_probabilities["tie"] * parry_tie_clash_outcomes["tie"]
		+ parry_outcome_probabilities["lose"]
		* parry_lose_clash_outcomes["tie"]
	)
	result["lose"] = (
		parry_outcome_probabilities["win"] * parry_win_clash_outcomes["lose"]
		+ parry_outcome_probabilities["tie"] * parry_tie_clash_outcomes["lose"]
		+ parry_outcome_probabilities["lose"]
		* parry_lose_clash_outcomes["lose"]
	)

	clash_dict[dynamic_key] = result
	return result

import time
start_time = time.time()
skill1 = Skill(2, tuple(['N', 'R', 'C'] * 3), 2, 0, 3)
skill2 = Skill(2, tuple(['N', 'N', 'N'] * 3), 2, 0, 3)
# print(clash(skill1, skill2, 0))
# print("Unique Clashes:", len(clash_dict))
# print("--- %s seconds ---" % (time.time() - start_time))

skill1_components = get_reduced_rolling_components(skill1.lose_skill)
for i in skill1_components:
	print(i)