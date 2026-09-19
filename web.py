from pyscript import when, document, display
from main import clash, Skill

@when("click", "#clash")
def update_all():
	base_power_1 = int(document.querySelector("#base-power-1").value)
	coin_power_1 = int(document.querySelector("#coin-power-1").value)
	coin_count_1 = int(document.querySelector("#coin-count-1").value)
	sanity_1 = int(document.querySelector("#sanity-1").value)
	paralysis_1 = int(document.querySelector("#paralysis-1").value)

	base_power_2 = int(document.querySelector("#base-power-2").value)
	coin_power_2 = int(document.querySelector("#coin-power-2").value)
	coin_count_2 = int(document.querySelector("#coin-count-2").value)
	sanity_2 = int(document.querySelector("#sanity-2").value)
	paralysis_2 = int(document.querySelector("#paralysis-2").value)

	skill1 = Skill(base_power_1, ('N') * coin_count_1, coin_power_1, sanity_1, paralysis_1)
	skill2 = Skill(base_power_2, ('N') * coin_count_2, coin_power_2, sanity_2, paralysis_2)

	try:
		result = clash(skill1, skill2, 0)
		
		document.querySelector("#overall-win-rate").innerHTML = f"{result.win_rates.overall_rate * 100:.2f}%"
		document.querySelector("#overall-tie-rate").innerHTML = f"{result.tie_rates.overall_rate * 100:.2f}%"
		document.querySelector("#overall-lose-rate").innerHTML = f"{result.lose_rates.overall_rate * 100:.2f}%"

	except Exception as e:
		print(e)
# fig, (ax1, ax2) = plt.subplots(2, sharex=True)
# ax1.bar([1, 2, 3], [0.5, 0.4, 0.1])
# ax1.set_xticks([1, 2, 3])
# ax2.bar([1, 2, 3, 4], [0.5, 0.4, 0.1, 0])
# ax2.set_xticks([1, 2, 3])
# plt.show()