RESOLVED: The writers time measurements are off

**Root Cause**: In `telemetry_real.py:101`, lap_time was incorrectly using `scor.mLapStartET` (lap start timestamp) instead of calculating the actual lap time as `scor.mCurrentET - scor.mLapStartET`.

**Fix**: Changed line 101 to: `'lap_time': scor.mCurrentET - scor.mLapStartET`

**Evidence**: 910s would be very slow for a lap of Sebring. I was doing closer to 2:10 (130s)

*** Lap 4 completed!
    Lap time: 910.819s
    Samples: 6501
    [OK] Saved to: telemetry_output\2025-11-19_20-47_Sebring_International_Raceway_The_Bend_Team_WRT_2025_#31_LM_Dean_Davids_lap4_t911s_20251119204548517080.csv
    Total laps saved: 13
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 174
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 424
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 674
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 926
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 1177
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 1427
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 1677
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 1929
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 2180
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 2430
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 2682
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 2935
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 3186
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 3437
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 3688
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 3938
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 4188
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 4439
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 4689
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 4941
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 5191
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 5441
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 5691
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 5942
[logging] Process: YES | Telemetry: YES | Lap: 4 | Samples: 6192

*** Lap 5 completed!
    Lap time: 1040.898s
    Samples: 6420
    [OK] Saved to: telemetry_output\2025-11-19_20-50_Sebring_International_Raceway_The_Bend_Team_WRT_2025_#31_LM_Dean_Davids_lap5_t1041s_20251119204758511620.csv
    Total laps saved: 14
