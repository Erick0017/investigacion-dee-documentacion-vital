-- Configuración focal separada; default Preview no abre Native.
return game:GetService("HttpService"):JSONDecode([=[
{
  "Schema": "DEE.SDK.Config.v0.1.0",
  "Version": "0.1.0",
  "Mode": "PREVIEW",
  "ExperienceId": "DEE_SDK_FOCAL",
  "SceneId": "CONSUME_RECHARGE",
  "AgentId": "FOCAL",
  "ScenarioFingerprint": "88c9583e47ea89bf2b4da429db3441c21775b4187ea928e33a9ad36cb9a9972c",
  "MaxOpportunities": 6,
  "MaxActions": 12,
  "Map": {
    "RootName": "DEE_FOCAL_SEIS_ZONAS",
    "Positions": {
      "0": [
        -54,
        8,
        38
      ],
      "1": [
        -54,
        8,
        -32
      ],
      "2": [
        -5,
        8,
        54
      ],
      "3": [
        0,
        8,
        -38
      ],
      "4": [
        51,
        8,
        38
      ],
      "5": [
        53,
        8,
        -29
      ]
    },
    "Obstacles": [
      {
        "Position": [
          0,
          8,
          10
        ],
        "Size": [
          12,
          6,
          18
        ]
      },
      {
        "Position": [
          27,
          8,
          -5
        ],
        "Size": [
          8,
          6,
          13
        ]
      }
    ],
    "Motor": {
      "WalkSpeed": 16,
      "AgentRadius": 2,
      "AgentHeight": 5,
      "AgentCanJump": false,
      "WaypointSpacing": 4,
      "ArrivalRadius": 2,
      "WaypointTimeout": 8,
      "MaxRecomputes": 2,
      "MaxWallSeconds": 45
    }
  },
  "PreviewPublicState": {
    "permissionStock": 18,
    "inventoryKey": false,
    "inventoryResource": false,
    "numberAPresent": false,
    "codeBPresent": false,
    "numberAVersion": 0,
    "codeBCurrent": false
  },
  "Scope": "SEPARATE FOCAL ENVIRONMENT; Preview counter18 is technical, not Native. Scope6 private backend required; no SDKdemo use.",
  "RunCycles": 6,
  "PrivateConnectionFolder": "DEE_FOCAL_PrivateConnection",
  "Transport": {
    "OperationPollSeconds": 900,
    "PollIntervalSeconds": 2,
    "MaxOperationRecords": 128,
    "StartupWaitSeconds": 900
  },
  "MapModule": "MapaFocal",
  "AdapterModule": "FocalAdapters",
  "Focal": {
    "schema": "DEE.SDK.FocalAvailability.Config.R01",
    "version": "0.1.0-focal-candidate",
    "frozenRule": "LOCAL_PORT_PASS_CONSUME_RECHARGE_3_ENVIRONMENT_EPOCHS",
    "maxCyclesPerArm": 6,
    "arms": [
      "CONSUME_RECHARGE",
      "NONCONSUMING_CONTROL"
    ],
    "startStation": 0,
    "rechargeEpochs": 3,
    "capacityPerPort": 1,
    "queryCost": 1,
    "emptyPortToll": 2,
    "initialStockFromBackend": true,
    "minimumPermissionStock": 18,
    "tagModeBothArms": "local_tag",
    "startEveryPortAvailable": true,
    "positions": {
      "0": [
        -54,
        8,
        38
      ],
      "1": [
        -54,
        8,
        -32
      ],
      "2": [
        -5,
        8,
        54
      ],
      "3": [
        0,
        8,
        -38
      ],
      "4": [
        51,
        8,
        38
      ],
      "5": [
        53,
        8,
        -29
      ]
    },
    "edges": {
      "0": {
        "0": 1,
        "1": 3
      },
      "1": {
        "0": 2,
        "1": 0
      },
      "2": {
        "0": 4,
        "1": 3
      },
      "3": {
        "0": 5,
        "1": 2
      },
      "4": {
        "0": 5,
        "1": 1
      },
      "5": {
        "0": 0,
        "1": 4
      }
    },
    "developmentOpportunities": [
      1,
      2,
      3,
      4
    ],
    "sealedReserveOpportunities": [
      5,
      6
    ],
    "nativePolicy": "UNCHANGED_OFFICIAL_ACTOR_ONLY",
    "tools": "NONE_FOR_FOCAL; no lessons or arithmetic; inherited product state not forged",
    "panelCodes": {
      "bothFree": 1,
      "onlyPort0Free": 0,
      "onlyPort1Free": 2,
      "bothPaid": "NOT_ENCODABLE; must never be current-station sample; stop if encountered"
    },
    "Arm": "CONSUME_RECHARGE"
  }
}
]=])
