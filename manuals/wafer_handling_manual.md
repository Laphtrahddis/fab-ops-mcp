# Wafer Handling Robot Manual (all tools)

## Page 1
Alarm WAFER_HANDLER_FAULT (critical). The transfer robot failed to pick or place a wafer, or a wafer was detected out of position. Likely causes: a misaligned end effector, a wafer that is warped or chipped, or a lost robot home position. Steps: stop the tool immediately and do not retry the move, because a retry can break the wafer. Open the load lock view port and confirm the wafer location. Re-home the robot from the maintenance screen, then run the robot teach check on each station. Report any broken wafer to the shift lead with the lot ID.
