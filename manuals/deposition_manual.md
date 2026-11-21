# CVD and PVD Deposition Tool Manual (CVD-01, PVD-01)

## Page 1
Overview. Chemical vapor deposition (CVD) grows thin films on the wafer from reacting gases at high temperature. Physical vapor deposition (PVD) sputters metal from a target onto the wafer. Both tools use heated chambers, precise gas flow control, and a vacuum system. Film thickness is checked on the metrology tool after every lot.

## Page 2
Alarm TEMP_DRIFT (warning). The heater temperature has drifted more than 3 degrees Celsius from the recipe setpoint for over 60 seconds. Likely causes: a failing heater zone, a thermocouple that is out of calibration, or a cooling water flow problem. Steps: compare all heater zone readings, check the cooling water flow meter, and recalibrate the thermocouple if one zone disagrees with the others. Hold the lot for a thickness check on the metrology tool before continuing.

## Page 3
Alarm GAS_FLOW_DEVIATION (warning). A mass flow controller (MFC) reading differs from its setpoint by more than 5 percent. Likely causes: a clogged MFC, a gas supply pressure drop, or a valve that is not fully open. Steps: check the gas cabinet supply pressure, run the MFC zero and span check, and swap the MFC if it fails the check. Film thickness on the current lot may be out of spec, so send it to metrology.

## Page 4
Alarm CHAMBER_DOOR_OPEN (info). The chamber or load lock door sensor reports open while the tool is idle. This is normal during maintenance. If it appears during production, check the door interlock sensor and make sure the door is fully closed and latched. The tool will not start a process while the interlock is open.
