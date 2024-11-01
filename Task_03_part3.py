#Q1: How much fuel can the vessel carry? 
#50 000 L 

#Q2: What is the estimated total range on a full tank? 
#1 engine half speed, ca. 50 days 

import numpy as np 
import matplotlib.pyplot as plt 

#-------------------------Required tank capasity-----------------------------------------------------#
#Tank capasity: 
tank_original_liters = 50000 #[L]

#Average fuel consumption based on RV Gunnerius visit: 
avg_fuel_consumption = 35.78 #[L/h]
avg_fuel_consumption_crew = 40 #[L/h]

#Maximum power required for voyage, theoretical: 
total_power_required = 450*3 #[kW]

#Energy density: 
energy_marine_diesel = 45.4 #[MJ/kg] given in engine data
energy_methanol = 22 #[MJ/kg], Link: https://www.methanology.com/mymethanol#no-back

ratio_energy_density = energy_marine_diesel / energy_methanol #[-], merine diesel devided on methanol 

#Density at 15 degrees celcius: 
density_marine_diesel = 820 #[kg/m^3]
density_methanol = 792 #[kg/m^3]

#Remember: 1 L = 0.001 m^3 and 1m^3 = 1000L 

#Task: Using the current tank size- the fuel consumption and the maximum power required for the voyage and stating all assumptions
#--> determine the tank size required

#Step 1: Calculate tank size in m^3:
tank_original_cubic = tank_original_liters * 0.001 

#Step 2: Estimate amount of diesel in [kg] at full tank capacity:
diesel_full_tank_kg = density_marine_diesel * tank_original_cubic

#Step 3: Estimate amount of methanol in [kg] at full tank capasity, based on same energy capacity requirement:
methanol_full_tank_kg = diesel_full_tank_kg * ratio_energy_density 

#Step 4: Calculate required tank capacity for equal amount of energy:
tank_methanol_cubic = methanol_full_tank_kg /density_methanol #[m^3]
tank_methanol_liters = tank_methanol_cubic * 1000 #[L]

#Solution: 
print(f'Required tank capacity for diesel: {np.round(tank_original_cubic, 3)} [m^3]')
print(f'Required tank capacity for diesel: {np.round(tank_original_liters, 3)} [L]')
print('\n')
print(f'Required tank capacity for methanol: {np.round(tank_methanol_cubic, 3)} [m^3]')
print(f'Required tank capacity for methanol: {np.round(tank_methanol_liters, 3)} [L]')
#----------------------------------------------------------------------------------------------------#


#-------------------------The max flow rate of fuel to the engine------------------------------------#
#Total power output at maximum load:
tot_power_output = 3*450 #[kW]

#Required energy produced at max load: 
tot_energy_output = tot_power_output * 3.6
print(tot_energy_output)

#Assumed thermal efficiency of Diesel-LNG engine: 
eta_thermal = 0.5 

#Required energy input at max load: 
tot_energy_input = tot_energy_output/eta_thermal
print(tot_energy_input)

#Required amount of methanol in [kg] needed to run engine at max capacity: 
methanol_per_hour_kg = tot_energy_input/energy_methanol

print(f'The max flow rate of fuel to the engine: {methanol_per_hour_kg} [kg/h]')
#----------------------------------------------------------------------------------------------------#