# Plasma Etch Chamber Maintenance Manual (ETCH-01, ETCH-02)

## Page 1
Overview. The plasma etch chamber removes material from the wafer surface using a radio-frequency (RF) plasma of process gases. Each chamber has an RF generator, a matching network, a vacuum system with a turbo pump, gas mass flow controllers, and a robotic wafer transfer arm. Always place the tool in maintenance mode on the MES before opening any panel. Only certified technicians may open the RF enclosure.

## Page 2
Alarm RF_REFLECTED_POWER_HIGH (critical). Reflected power above 10 percent of forward power means the plasma is not absorbing RF energy correctly. Likely causes: a worn or drifting matching network capacitor, a loose RF cable, or a polymer build-up on the chamber walls. Steps: stop the current lot, check the RF cable torque, run the matching network auto-tune, and if reflected power stays high, schedule a wet clean of the chamber. Do not restart production until reflected power is below 5 percent.

## Page 3
Alarm VACUUM_LEAK (critical). The chamber cannot reach base pressure below 5 millitorr within 10 minutes. Likely causes: a damaged O-ring on the chamber lid, a cracked viewport, or a leaking gas line fitting. Steps: put the tool in maintenance mode, run the rate-of-rise leak check, then use the helium leak detector around the lid O-ring and gas fittings. Replace the O-ring if the leak is at the lid. A leak rate above 20 millitorr per minute requires the tool to stay down.

## Page 4
Alarm PRESSURE_HIGH (warning). Process pressure is more than 10 percent above the recipe setpoint. Likely causes: a sticking throttle valve, a slow turbo pump, or a gas flow above setpoint. Steps: check the throttle valve position log, verify turbo pump speed, and compare gas flows against the recipe. If the throttle valve is sticking, cycle it three times from the maintenance screen.

## Page 5
Preventive maintenance (PM_DUE_SOON, info). The etch chamber needs a wet clean every 3000 RF hours and an O-ring replacement every 6 months. When PM_DUE_SOON appears, the tool has less than 50 RF hours left before its scheduled PM. Plan the PM with the shift lead so that no hot lots are queued on the tool.
