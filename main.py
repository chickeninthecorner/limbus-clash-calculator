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


class BasicSkill:
	def __init__(
		self, base_power, coin_count, coin_power, sanity, paralysis=0
	):
		self.base_power = base_power
		self.coin_count = coin_count
		self.coin_power = coin_power
		self.sanity = sanity
		self.paralysis = paralysis

	@property
	def static_id(self):
		return (self.base_power, self.coin_count, self.coin_power, self.sanity)

	@property
	def dynamic_id(self):
		return (
			self.base_power,
			self.coin_count,
			self.coin_power,
			self.sanity,
			self.paralysis,
		)

	@property
	def effective_dynamic_id(self):
		return (
			self.base_power,
			self.coin_count,
			self.coin_power,
			self.sanity,
			min(self.paralysis, self.coin_count),
		)

	@property
	def lose_skill(self):
		result = copy.copy(self)
		result.coin_count -= 1
		result.paralysis = max(self.paralysis - self.coin_count, 0)
		return result

	@property
	def next_skill(self):
		result = copy.copy(self)
		result.paralysis = max(self.paralysis - self.coin_count, 0)
		return result


def get_divided_skill(skill):
	# divides a skill into paralyzed and non paralyzed coins if possible
	paralysis = skill.paralysis
	state = {}

	result = []
	result.append(BasicSkill(skill.base_power, 1, 0, 0, -50))
	consecutive_coins = 0

	def append_skill():
		if state["paralyzed"]:
			result.append(BasicSkill(0, consecutive_coins, 0, -50))
		else:
			result.append(
				BasicSkill(
					0, consecutive_coins, skill.coin_power, skill.sanity
				)
			)

	for coin in range(skill.coin_count):
		new_state = {}
		if paralysis > 0:
			new_state["paralyzed"] = True
		else:
			new_state["paralyzed"] = False

		if state == {}:
			state = new_state
			consecutive_coins = 1
		elif state == new_state:
			consecutive_coins += 1
		else:
			append_skill()

			consecutive_coins = 1
			state = new_state

		paralysis = max(paralysis - 1, 0)

	append_skill()

	return result


combined_power_probabilities_dict = {}


def get_combined_power_probabilities(
	power_probabilities1, power_probabilities2
):
	key = (power_probabilities1.items(), power_probabilities2.items())
	if key in combined_power_probabilities_dict:
		return combined_power_probabilities_dict(key)

	result = {}

	for power1 in power_probabilities1:
		for power2 in power_probabilities2:
			combined_power = power1 + power2
			combined_probability = (
				power_probabilities1[power1] * power_probabilities2[power2]
			)
			if combined_power not in result:
				result[combined_power] = 0.0

			result[combined_power] = combined_probability

	combined_power_probabilities_dict[key] = result
	return result


power_probabilities_dict = {}


def get_power_probabilities(skill):
	if skill.effective_dynamic_id in power_probabilities_dict:
		return power_probabilities_dict[skill.effective_dynamic_id]
	else:
		effective_coin_power = skill.coin_power

	heads_probability = skill.sanity / 100 + 0.5
	tails_probability = 1 - heads_probability

	result = {}

	for head_count in range(0, skill.coin_count + 1):
		tail_count = skill.coin_count - head_count

		power = skill.base_power + effective_coin_power * head_count
		power = max(power, 0)
		probability = (
			heads_probability**head_count
			* tails_probability**tail_count
			* combination(skill.coin_count, head_count)
		)
		result[power] = probability

	power_probabilities_dict[skill.effective_dynamic_id] = result
	return result


outcome_probabilities_dict = {}


def get_parry_outcome_probabilities(skill1, skill2):
	effective_dynamic_key = (skill1.effective_dynamic_id, skill2.effective_dynamic_id)
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

	parry_win_clash_outcomes = clash(skill1.next_skill, skill2.lose_skill, parry + 1)
	parry_lose_clash_outcomes = clash(skill1.lose_skill, skill2.next_skill, parry + 1)
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


skill1 = BasicSkill(1, 50, 1, 45)
skill2 = BasicSkill(1, 50, 1, 45)
print(clash(skill1, skill2, 0))
print(len(clash_dict))