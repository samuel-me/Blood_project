


import requests

def predict(current_month,months_since_joined,recency,total_donations,eligible):
  """
  Current month = corrent month of the year  in munbers, e.g  january = 1 ( integer)
  Months since Joined = number  of tmonths  since the user regustered. e,g if they Jouned in januray and this is  August, the number = 7 ( Jan - August)
  recency = how many months since the last time they donated. 3 = 3 months  ago
  total donatins = all the times they donated 
  eligibility  is dependent on recency so any one whose recency is higer than 2 is eligible. 1 = True, 0 = false 

  Output to probability to donate 
  """

  response = requests.post(
      "https://blood-project-1.onrender.com/predict",
      json={
          "as_of_month": current_month,
          "months_since_joined": months_since_joined,
          "recency_months": recency,
          "frequency_total_donations": total_donations,
          "eligible_this_month": eligible
      }
  )
  return response.json()['prediction']  



import pandas as  pd

# The location of the requester 
recipient_location = "Hobart"
recipient_blood_group = "A+"


# This is  an example dataset thoguh , the neame needs to be changed 
data = pd.read_csv("/content/blood_donor_dataset.csv")

# Filter by location 
new_data = data[data['city'] == recipient_location]

# Filter by Blood Group 
if recipient_blood_group == "O+":
  # O- and O +
  final_data = new_data[(new_data['blood_group'] == "O-") | (new_data['blood_group'] == "O+")]

if recipient_blood_group == "O-":
  # Only O-
  final_data = new_data[new_data['blood_group'] == "O-"]

if recipient_blood_group == "A+":
  # O-, O-,a+, A- 
  final_data = new_data[(new_data['blood_group'] == "O-") | (new_data['blood_group'] == "O+") | (new_data['blood_group'] == "A+") | (new_data['blood_group'] == "A-")]

if recipient_blood_group == "A-":
  #O-, A-
  final_data = new_data[(new_data['blood_group'] == "O-") | (new_data['blood_group'] == "A-")]

if recipient_blood_group == "B+":
  # o+, O-, B+, B-
  final_data = new_data[(new_data['blood_group'] == "O-") | (new_data['blood_group'] == "O+") | (new_data['blood_group'] == "B+") | (new_data['blood_group'] == "B-")]

if recipient_blood_group == "B-":
  # O- and B-
  final_data = new_data[(new_data['blood_group'] == "O-") | (new_data['blood_group'] == "B-")]

if recipient_blood_group == "AB+":
  # ALL blood groups 
  final_data = new_data # all blood groups 

if recipient_blood_group == "AB-":
  # AB-, B-, O-, A-
  final_data = new_data[(new_data['blood_group'] == "O-") | (new_data['blood_group'] == "B-")  | (new_data['blood_group'] == "A-") | (new_data['blood_group'] == "AB-")]

# Then we pass everyone remianing in the sheet inside the modle one by one 


result = []
final_data = final_data.reset_index()
for i in range(len(final_data)):
  id = final_data.loc[i]['donor_id']
  current_month = final_data.loc[i]["as_of_month"].item()
  months_since_joined= final_data.loc[i]['months_since_joined'].item()
  recency = final_data.loc[i]["recency_months"].item()
  total_donations = final_data.loc[i]["frequency_total_donations"].item()
  eligible = final_data.loc[i]["eligible_this_month"].item()

  prediction = predict(current_month, months_since_joined, recency, total_donations, eligible)
  # pass all these in  the prediction model
  result.append({id:prediction})

# sorts them in decending order 
sorted_result = sorted_data = sorted(result, key=lambda x: list(x.values())[0], reverse=True)

