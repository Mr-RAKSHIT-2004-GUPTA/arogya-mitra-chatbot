import json
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# --- Load the new, richer medicine database ---
with open('medicines_plus.json', 'r') as f:
    medicine_db = json.load(f)

class ActionProvidePlantFirstAid(Action):

    def name(self) -> Text:
        return "action_provide_plant_first_aid"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        injury_entity = next(tracker.get_latest_entity_values("plant_injury"), None)

        if not injury_entity:
            dispatcher.utter_message(text="I can help with first aid. Please tell me if the injury is a burn, a cut, or from gas inhalation.")
            return []

        injury = injury_entity.lower()

        if "burn" in injury:
            dispatcher.utter_message(response="utter_first_aid_burn")
        elif "cut" in injury:
            dispatcher.utter_message(response="utter_first_aid_cut")
        elif "gas" in injury or "fume" in injury:
            dispatcher.utter_message(response="utter_first_aid_gas")
        else:
            dispatcher.utter_message(text=f"I don't have specific first-aid information for '{injury_entity}'. For any serious injury, please contact your plant's medical team immediately.")

        return []

# --- NEW: Arogya Nidhi Custom Action ---

class ActionFindAffordableMedicine(Action):

    def name(self) -> Text:
        return "action_find_affordable_medicine"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the medicine name entity from the user's message
        medicine_name_entity = next(tracker.get_latest_entity_values("medicine_name"), None)
        
        disclaimer = "\n\n**DISCLAIMER:** Do not change your medication without consulting a qualified doctor. Prices are estimates and may vary."

        if not medicine_name_entity:
            dispatcher.utter_message(text="Sure, please tell me the name and strength of the medicine you're looking for (e.g., 'Calpol 500').")
            return []

        # --- Search Logic ---
        found_composition = None
        user_input_lower = medicine_name_entity.lower()

        # Iterate through the entire database to find a match
        for composition in medicine_db:
            for brand in composition['brands']:
                if brand['brand_name'].lower() in user_input_lower:
                    found_composition = composition
                    break
            if found_composition:
                break
        
        # --- Formatting the Output ---
        if found_composition:
            response_text = f"Searching for cost-effective alternatives for **{medicine_name_entity}** ({found_composition['generic_name']} {found_composition['strength']})...\n\n"
            response_text += "Here are a few options with the same composition:\n\n"
            
            for brand in found_composition['brands']:
                response_text += f"- **{brand['brand_name']}** by {brand['manufacturer']}\n"
                response_text += f"  (Est. Price: ₹{brand['estimated_mrp']}) - *{brand['notes']}*\n"
            
            response_text += "\n💡 **Savings Tip:** You can discuss these options with your doctor to find the most suitable and affordable choice."
            response_text += disclaimer
        else:
            response_text = f"I'm sorry, I couldn't find information for '{medicine_name_entity}'. Please check the spelling and include the strength (e.g., 'Dolo 500')."
            response_text += disclaimer
            
        dispatcher.utter_message(text=response_text)

        return []