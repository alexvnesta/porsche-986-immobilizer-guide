# Porsche 986/996 ACU Wiring & Connector Information

## ACU Connector Pinout

The ACU (Alarm Control Unit) uses a large multi-pin connector. Pin numbering varies by model year.

### M535 (Pre-2001) Connector

| Pin | Wire Color | Function |
|-----|------------|----------|
| 1 | Black (shielded) | Antenna signal |
| 2 | - | Central locking motor driver |
| 3 | - | Central locking motor driver |
| 4 | - | Window control |
| 5 | - | Window control |
| 6 | - | Interior light control |
| 7 | - | Door contact (driver) |
| 8 | - | Door contact (passenger) |
| ... | ... | ... |
| 22 | Black (shielded) | Antenna ground |
| ... | ... | ... |

**Note:** Pins 1 and 22 run together in a black sheath (antenna signal + ground shielding).

### Antenna Wiring Configuration

#### Pre-2001 (M535 early version)
```
Pin 1  ──────┐
             ├── Black sheathed cable to antenna
Pin 22 ──────┘
```

#### Post-2001 (M535 later version)
Different antenna configuration - check specific documentation.

### Wiring Differences Between Versions

| Feature | Pre-2001 (996.618.260.xx) | Post-2001 (996.618.262.xx) |
|---------|---------------------------|----------------------------|
| Electronic frunk | No | Yes |
| Antenna pins | 1 + 22 | Different configuration |
| Window control | Basic | Enhanced |
| Direct swap | No | No |

**Important:** The two versions are NOT directly interchangeable due to wiring differences.

## K-Line Diagnostics

The ACU communicates via K-line (ISO 9141) for diagnostics.

| Connection | Pin |
|------------|-----|
| K-Line | OBD-II Pin 7 |
| Ground | OBD-II Pin 4, 5 |
| +12V | OBD-II Pin 16 |

## Antenna Location

The transponder antenna is located around the ignition barrel. It reads the ID48 chip in the key head when the key is inserted.

```
┌─────────────────┐
│   Ignition      │
│   ┌─────────┐   │
│   │  Key    │   │
│   │ Insert  │   │  ← Antenna coil surrounds this area
│   │  Here   │   │
│   └─────────┘   │
└─────────────────┘
```

## RF Remote Antenna

The RF antenna for the remote control function is separate from the transponder antenna.

- **Frequency:** 315 MHz (USA) or 433 MHz (EU)
- **Location:** Connected to ACU via pins 1 and 22 (early models)
- **Type:** Typically a wire antenna or PCB trace antenna

## Fuse Information

| Fuse | Rating | Function |
|------|--------|----------|
| ACU main | 15A | Main power to ACU |
| Central locking | 20A | Door lock motors |

**Note:** There's also a fuse on the back of the ACU board itself that controls central locking.

## Ground Points

The ACU requires good ground connections. Check these if experiencing intermittent issues:

1. Main ground at ACU connector
2. Body ground under driver's seat
3. Battery negative terminal

## Common Wiring Issues

### Water Damage Symptoms

When water enters the ACU area:

1. **Immediate:** ACU shorts, alarm may trigger
2. **Corrosion:** Intermittent operation, then failure
3. **Common failures:**
   - Central locking stops working
   - Windows operate randomly
   - Remote stops responding
   - Car won't start (immobilizer failure)

### Connector Corrosion

The ACU connector can develop corrosion, especially in humid climates or after water exposure.

**Treatment:**
1. Disconnect battery
2. Remove ACU connector
3. Clean pins with DeoxIT or electrical contact cleaner
4. Apply dielectric grease
5. Reconnect

### Antenna Issues

If remote range is reduced:

1. Check antenna connection at ACU
2. Inspect antenna wire for damage
3. Verify pins 1 and 22 continuity
4. Check antenna mounting/positioning

## Relay Information

The ACU controls several relays:

| Relay | Function |
|-------|----------|
| Central locking | Door lock motors |
| Interior lights | Dome light control |
| Alarm siren | External alarm |

These relays are typically external to the ACU but controlled by it.

## Immobilizer Communication

### ACU to DME Communication

The ACU and DME (Engine Control Unit) communicate to verify key authorization:

```
┌─────────┐                    ┌─────────┐
│   ACU   │ ←── K-Line ────→   │   DME   │
│ (Alarm) │                    │(Engine) │
└─────────┘                    └─────────┘
     ↑                              ↑
     │                              │
Transponder                    Fuel/Spark
  reading                       enable
```

**Sequence:**
1. Key inserted, transponder read by antenna
2. ACU verifies transponder ID
3. ACU sends authorization to DME
4. DME enables fuel injection and ignition

### Diagnostic Communication

```
┌──────────┐      ┌─────────┐      ┌─────────┐
│  PIWIS   │ ──→  │  OBD-II │ ──→  │   ACU   │
│          │      │  Port   │      │         │
└──────────┘      └─────────┘      └─────────┘
                       │
                       ↓
                  ┌─────────┐
                  │   DME   │
                  └─────────┘
```

## Testing Procedures

### Testing Antenna

1. Measure resistance between pins 1 and 22
   - Should be low resistance (antenna coil)
   - Open circuit = broken antenna

2. Check for short to ground
   - Neither pin should be shorted to ground

### Testing Remote Signal

Use an RF detector or SDR to verify remote is transmitting:

- **USA frequency:** 315 MHz
- **EU frequency:** 433.92 MHz
- **Modulation:** OOK (On-Off Keying)

### Testing K-Line

1. Key ON, engine OFF
2. Measure voltage at OBD-II pin 7
3. Should be approximately 12V when idle
4. Will pulse when communicating

## Waterproofing Solutions

To prevent future water damage:

1. **ECU Doctors Waterproof Case**
   - Aftermarket enclosure for ACU
   - Mounts in same location
   - Completely waterproof

2. **DIY Conformal Coating**
   - Remove ACU board
   - Apply conformal coating spray
   - Protects against moisture
   - Does NOT protect against immersion

3. **Relocate ACU**
   - Move ACU to higher location
   - Requires extending wiring harness
   - Not recommended without experience
