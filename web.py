from pyscript import when, document
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
		
		output_html = f"Skill 1: {base_power_1}+{coin_power_1}x{coin_count_1}\
			<br>Skill 2: {base_power_2}+{coin_power_2}x{coin_count_2}\
			<br>\
			<br>Win rate: {round(result.win_rates.overall_rate * 100, 3)}%\
			<br>Lose rate: {round(result.lose_rates.overall_rate * 100, 3)}%"
		
		document.querySelector("#display").innerHTML = output_html
	except:
		pass