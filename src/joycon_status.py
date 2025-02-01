from pyjoycon import JoyCon, get_R_id, get_L_id

joycon_R_id = get_R_id()
if joycon_R_id is not None:
    print("Joy-Con (R): ", joycon_R_id)
joycon_L_id = get_L_id()
if joycon_L_id is not None:
    print("Joy-Con (L): ", joycon_L_id)

joycon_R = JoyCon(*joycon_R_id)
joycon_R.get_status()

joycon_L = JoyCon(*joycon_L_id)
joycon_L.get_status()