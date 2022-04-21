#%%
import pandas as pd
import simplejson as json

#%%

df = pd.read_csv("https://vaccinedata.covid19nearme.com.au/data/geo/air_sa3.csv")
# 'DATE_AS_AT', 'AGG_LEVEL', 'STATE', 'ABS_CODE', 'ABS_NAME', 'AGE_LOWER',
# 'AGE_UPPER', 'AIR_FIRST_DOSE_PCT', 'AIR_SECOND_DOSE_PCT', 'AIR_THIRD_DOSE_PCT',
# 'AIR_THIRD_DOSE_ELIGIBLE_PCT', 'AIR_FIRST_DOSE_APPROX_COUNT',
# 'AIR_SECOND_DOSE_APPROX_COUNT', 'AIR_THIRD_DOSE_APPROX_COUNT', 
# 'ABS_ERP_2019_POPULATION', 'VALIDATED', 'URL'

df.sort_values('DATE_AS_AT', inplace=True)

p = df

print(p)
print(p.columns.tolist())

#%%

with open("sa3-codes.json") as json_file:
	sa3id = json.load(json_file)
#%%
df = df.rename(columns={"DATE_AS_AT":"date", "AIR_FIRST_DOSE_PCT":"first dose", "AIR_SECOND_DOSE_PCT":"second dose", 'AIR_THIRD_DOSE_PCT':'third dose'})
#%%
df = df[["date", "ABS_CODE", "ABS_NAME", "STATE", "first dose", "second dose", 'third dose']]

# %%

# fully = rates.drop(['At_least_one_dose_15'], axis=1)

pvt_fully = df.pivot(index=['ABS_CODE','ABS_NAME', "STATE"], columns=['date'], values=['second dose'])
pvt_fully.columns = pvt_fully.columns.droplevel()
pvt_fully = pvt_fully.reset_index()
# pvt_fully['change-weekly'] = pvt_fully.iloc[:,-1] - pvt_fully.iloc[:,-2]

#%%

pvt_partly = df.pivot(index=['ABS_CODE','ABS_NAME', "STATE"], columns=['date'], values=['first dose'])
pvt_partly.columns = pvt_partly.columns.droplevel()
pvt_partly = pvt_partly.reset_index()

#%%

pvt_third = df.pivot(index=['ABS_CODE','ABS_NAME', "STATE"], columns=['date'], values=['third dose'])
pvt_third.columns = pvt_third.columns.droplevel()
pvt_third = pvt_third.reset_index()
pvt_third['change-weekly'] = pvt_third.iloc[:,-1] - pvt_third.iloc[:,-2]

#%%
# last_date = pvt_fully.columns[-2]
last_date = pvt_third.columns[-2]

# final = pvt_fully[["ABS_CODE", "ABS_NAME", "STATE",last_date,'change-weekly']]
final = pvt_third[["ABS_CODE", "ABS_NAME", "STATE",last_date,'change-weekly']]

# final = final.rename(columns={"ABS_CODE":"id","ABS_NAME":"Name",last_date:"fully_vaccinated"})
final = final.rename(columns={"ABS_CODE":"id","ABS_NAME":"Name",last_date:"boostered"})

# final['id'] = final['Name'].map(sa4id) 

# final_map = final[['id','Name', "fully_vaccinated", 'change-weekly']]
final_map = final[['id','Name', "boostered", 'change-weekly']]

final_map["at_least_one_dose"] = pvt_partly[last_date]
final_map['two_doses'] = pvt_fully[last_date]

final_map = final_map.round(1)
final_map = final_map.astype(str)


#%%
final_table = final_map.copy()

final_table = final_table.drop(['id'], axis=1)

final_table = final_table.rename(columns={"SA4":"Name","two_doses":"Two doses","at_least_one_dose":"At least one dose (15+)","boostered":"Boostered", 'change-weekly':"Week-on-week booster change"})

final_table.sort_values(["Week-on-week booster change"], ascending=False, inplace=True)

# final_table = final_table.round(1)

#%%
pvt_fully.to_csv("fully-change.csv")

final_map.to_csv("final-map.csv")
final_table.to_csv("final-table.csv")

#%%

from syncMap import syncMap

def makeMap(df):
	
	settings = [
				{
					"title": "Vaccination rates by area in Australia",
					"subtitle": "Showing the current vaccination rates by SA3 area, as well as the weekly  increase in the percentage of people aged 15 and over who are boostered. Last updated {date}".format(date=last_date),
					"footnote": "",
					"source": "Department of Health, scraped by Ken Tsang",
					"boundary":"https://interactive.guim.co.uk/gis/sa3.json",
					"place":"au"
				}
			]
	
	mapping = [
		{"data":"boostered","display":"Boostered","values":"","colours":"#ffeda0, #800026","tooltip":"<strong>{{Name}}</strong><br>Boostered: <b>{{boostered}}%</b><br>Two doses: <b>{{two_doses}}%</b><br>At least one dose (15+): <b>{{at_least_one_dose}}%</b>","scale":"linear","keyText":"% vaccinated"},
	{"data":"two_doses","display":"Two doses","values":"","colours":"#ffeda0, #800026","tooltip":"<strong>{{Name}}</strong><br>Two doses: <b>{{two_doses}}%</b><br>At least one dose (15+): <b>{{at_least_one_dose}}%</b>","scale":"linear","keyText":"% vaccinated"},	
		{"data":"change-weekly","display":"Weekly booster increase","values":"","colours":"#ffffd9, #225ea8","tooltip":"<strong>{{Name}}</strong><br>Weekly increase: <b>{{change-weekly}} pp</b><br>At least one dose (15+): <b>{{at_least_one_dose}}%</b>","scale":"linear","keyText":"% point increase"},
{"data":"at_least_one_dose","display":"At least one dose (15+)","values":"","colours":"#ffeda0, #800026","tooltip":"<strong>{{Name}}</strong><br>Two doses: <b>{{two_doses}}%</b><br>At least one dose (15+): <b>{{at_least_one_dose}}%</b>","scale":"linear","keyText":"% vaccinated"}
]
	
	mapData = df.to_dict('records')
	syncMap(settings=settings, data=mapData, mapping=mapping, chartName="1loQxWCqzcor1aJpIUdZPX4fqq2KJIcjbIiTnMrIk0oQ-2")


makeMap(final_map)

#%%

from yachtcharter import yachtCharter
# testo = '-testo'
testo = ''

def makeTable(df):
	
	template = [
			{
				"title": "Increase in vaccination rates by SA3 areas for people aged 15 and over",
				"subtitle": "Showing the increase in the percentage of people aged 15 and over who have received at least one dose. The highest value for each column is 95. Last updated {date}".format(date=last_date),
				"footnote": "",
				"source": "Department of Health",
			}
		]
	key = []
	periods = []
	labels = []
	chartId = [{"type":"table"}]
	key = [{"key":"Boostered","values":"","colours":"#ffeda0, #800026","scale":"linear"},
		{"key":"Two doses","values":"","colours":"#ffeda0, #800026","scale":"linear"},
{"key":"Week-on-week booster change","values":"","colours":"#fff7bc, #993404","scale":"linear"},
{"key":"At least one dose (15+)","values":"","colours":"#ffeda0, #800026","scale":"linear"}]
# 	df.fillna('', inplace=True)
# 	df = df.reset_index()
	chartData = df.to_dict('records')
	options = [{"format":"scrolling","enableSearch":"TRUE","enableSort":"TRUE"}]
	yachtCharter(template=template, data=chartData, options=options, chartId=chartId, chartName=f"change-in-vax-rates-sa3-table{testo}", key=key)

makeTable(final_table)



print(final_table)