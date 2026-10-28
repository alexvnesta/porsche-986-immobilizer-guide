# Porsche 986/996 ACU Wiring & Connector Information

The Alarm Control Unit (ACU / Immobilizer) is located on the cabin floor **directly under the driver's seat** (left side on LHD cars, right side on RHD cars).

The unit interfaces with the vehicle harness through two multi-pin connectors:
- **Connector I / A (42-Pin Yellow/Black Connector):** Low-current signal lines, microswitch inputs, K-line diagnosis, and the DME immobilizer W-lead.
- **Connector II / B (12-Pin High-Current Connector):** Battery power (Terminal 30), chassis ground, central locking motors, horn, and turn signal flasher outputs.

---

## 1. Complete 54-Pin Connector Pinouts

There are two major production generations of the ACU:
1. **Early Generation (MY1997–2000):** Part numbers `996.618.260.xx` / `986.618.260.xx` (cable-operated manual front and rear luggage lid releases).
2. **Late Facelift Generation (MY2001–2005):** Part numbers `996.618.262.xx` / `986.618.262.xx` (electronic luggage release switches on the door threshold sill).

### Connector I / A (42-Pin Signal & Diagnostic Connector)

| Pin | Early Function (260) | Late Function (262) | Wire Size | Wire Color | Notes & Destination |
|:---:|:---|:---|:---:|:---:|:---|
| **A01** | Antenna Screen Signal | Seat Memory Data | 0.5 mm² | WH/VI | **CRITICAL DIFFERENCE:** Coaxial RF antenna on early; driver seat memory serial bus on late. |
| **A02** | Diagnosis K-Lead | Diagnosis K-Lead | 0.35 mm² | OG/BK | Diagnostic K-Line to **OBD-II Pin 7** (ISO 14230 fast init address `0xC0`). |
| **A03** | Signal Transformer Data | Signal Transformer Data | 0.5 mm² | GN/WH | Inductive antenna coil around ignition key barrel (Megamos ID48 reading). |
| **A04** | Control Signal Transformer | Control Signal Transformer | 0.5 mm² | GN/BK | Inductive antenna coil around ignition key barrel. |
| **A05** | Door Safe Driver's Side | Door Safe Driver's Side | 0.5 mm² | BN/YE | Microswitch in driver door lock assembly (deadbolt safe verification). |
| **A06** | Convertible Top Open/Close | Convertible Top Open/Close | 0.5 mm² | RE/WH | Interlock signal to convertible soft-top double relay. |
| **A07** | Door Contact Passenger | Door Contact Passenger | 0.5 mm² | BN/VI | Passenger door open/closed microswitch (window drop & interior lights). |
| **A08** | Interior Sensor Data Send | Interior Sensor Data Send | 0.5 mm² | YE/BK | TX serial data line to cockpit radar interior monitoring sensor. |
| **A09** | *Not Connected* | Button Cover Unlocking | 0.5 mm² | BN/BK | **DIFFERENCE:** Door sill switch input for electronic front trunk release. |
| **A10** | Central Lock Button Open | Cover Open Display | 0.5 mm² | WH/YE | **DIFFERENCE:** Early = dash button open; Late = sill button "lid open" warning LED. |
| **A11** | External Shift Contact | External Shift Contact | 0.5 mm² | BL/RE | Tiptronic shift-gate position microswitch. |
| **A12** | *Not Connected* | Airbag Crash Input | 0.5 mm² | WH/BK | **CRITICAL DIFFERENCE:** Airbag trigger input moved here on late cars (was A33 on early). |
| **A13** | Cover Rear Contact | Cover Rear Contact | 0.5 mm² | BN/GY | Engine compartment lid / rear luggage trunk closed microswitch. |
| **A14** | Speed Sensor | Speed Sensor | 0.5 mm² | WH/RE | Speedometer pulse from instrument cluster (triggers > 3 km/h autolock). |
| **A15** | Door Lock Cylinder Unlock | Door Lock Cylinder Unlock | 0.5 mm² | BK/OG | Key cylinder mechanical unlock microswitch. |
| **A16** | Terminal 86S | Terminal 86S | 0.5 mm² | OG | Key inserted into ignition lock barrel (switched +12V from ignition switch). |
| **A17** | Rear Luggage Compartment Light | Glove Box Contact | 0.5 mm² | BN/BL | **DIFFERENCE:** Early = trunk lamp circuit; Late = oddments / glove compartment switch. |
| **A18** | Power Window Comfort Control | Power Window Comfort Control | 0.5 mm² | GN | One-touch comfort window lower/raise signal. |
| **A19** | Safe Motor Close | Safe Motor Close | 0.5 mm² | BN/BL | Door latch deadbolt motor actuator drive. |
| **A20** | *Not Connected* | *Not Connected* | — | — | Spare pin. |
| **A21** | *Not Connected* | *Not Connected* | — | — | Spare pin. |
| **A22** | Screen Antenna Ground | Targa Roof Flap | 0.5 mm² | BN/GN | **DIFFERENCE:** Early = RF antenna ground shield; Late = 996 Targa rear glass roof flap. |
| **A23** | W-Lead (DME Immobilizer) | W-Lead (DME Immobilizer) | 0.5 mm² | GN | **CRITICAL:** Bidirectional serial handshake line to DME (Pin IV/31 on ME7.2 / Pin III/31 on ME5.2.2). |
| **A24** | Interior Sensor Data Receive | Interior Sensor Data Receive | 0.5 mm² | YE/GN | RX serial data line from cockpit radar interior monitoring sensor. |
| **A25** | Door Contact Driver's Side | Door Contact Driver's Side | 0.5 mm² | BN/YE | Driver door open/closed microswitch (window drop & interior lights). |
| **A26** | Package Tray / Oddments Box | Package Tray / Oddments Box | 0.5 mm² | BN/BL | Center console storage bin anti-theft microswitch. |
| **A27** | Radio Ground Contact | Radio Ground Contact | 0.5 mm² | BN/BU | Factory stereo anti-theft ground clip contact. |
| **A28** | Door Safe Passenger's Side | Door Safe Passenger's Side | 0.5 mm² | BN/WH | Microswitch in passenger door lock assembly. |
| **A29** | Central Lock Button Close | Central Close/Open Button | 0.5 mm² | BK/WH | **DIFFERENCE:** Early = separate close input; Late = single combined toggle switch. |
| **A30** | Door Locked Driver's Side | Door Locked Driver's Side | 0.5 mm² | BN/VI | Driver door locked microswitch status. |
| **A31** | Cover Front Contact | Cover Front Contact | 0.5 mm² | BN/GN | Front luggage trunk lid closed microswitch. |
| **A32** | Door Locked Passenger's Side | Door Locked Passenger's Side | 0.5 mm² | BN/GN | Passenger door locked microswitch status. |
| **A33** | **Airbag Crash Sensor Input** | **Front Trunk Opener Actuator** | 0.75 mm² | WH/BK | ⚠️ **DANGEROUS PIN CONFLICT:** Early = Airbag trigger; Late = Electronic frunk solenoid! |
| **A34** | Tailgate Opener Actuator | Tailgate Opener Actuator | 0.75 mm² | GN/BK | Electronic rear luggage compartment release solenoid. |
| **A35** | Door Lock Cylinder Close | Door Lock Cylinder Close | 0.5 mm² | BK/GN | Key cylinder mechanical lock microswitch. |
| **A36** | Terminal 15 (+12V Switched) | Terminal 15 (+12V Switched) | 0.75 mm² | BK/RE | Switched ignition power (hot in run/start). |
| **A37** | Luggage Compartment Light | Luggage Compartment Light | 0.75 mm² | BN/BK | Switched ground path for front/rear trunk illumination lamps. |
| **A38** | External Electronic Control | External Electronic Control | 0.5 mm² | GN/YE | Auxiliary control output. |
| **A39** | Function Indicator LED | Function Indicator LED | 0.5 mm² | RE/BK | Anti-theft flashing status LEDs (door lock buttons & dash cluster). |
| **A40** | Comfort Open Windows | Comfort Open Windows | 0.5 mm² | GN/RE | Remote key hold-down window drop signal. |
| **A41** | Door Locked Display LED | Door Locked Display LED | 0.5 mm² | RE/WH | Central locking dash button illumination LED. |
| **A42** | Comfort Close Windows | Comfort Close Windows | 0.5 mm² | GN/BL | Remote key hold-down window roll-up signal. |

---

### Connector II / B (12-Pin High-Current Connector)

Connector B supplies high-current actuators and main system power:

| Pin | Signal Name | Wire Size | Wire Color | Destination & Function |
|:---:|:---|:---:|:---:|:---|
| **B01** | Terminal 31 (Chassis Ground) | 2.5 mm² | BN | Direct chassis ground point under driver's seat. |
| **B02** | Alarm Horn / Siren Output | 1.5 mm² | BN/WH | High-current switched +12V drive to dedicated alarm horn in battery tray. |
| **B03** | Central Locking Common Return | 1.5 mm² | BN/GN | Bi-directional H-bridge return line for door lock motors. |
| **B04** | Consumer Cutoff | 1.0 mm² | RE/BK | Battery-saver relay (de-energizes interior lights after 20 minutes). |
| **B05** | Fuel Tank Flap Motor Open | 1.0 mm² | GN/YE | Electric actuator motor to unlock fuel filler door. |
| **B06** | Turn Signal Left Output | 1.5 mm² | BK/WH | Direct drive to left exterior turn signal bulbs (hazard alarm flasher). |
| **B07** | Terminal 30 (Battery +12V) | 2.5 mm² | RE/GN | Constant unswitched +12V battery power supply (Fuse C3 / D8). |
| **B08** | Terminal 30 Switched Consumer | 1.5 mm² | RE/BL | Switched battery feed to auxiliary cabin loads. |
| **B09** | Door Locking Motors Lock Drive | 1.5 mm² | BN/YE | High-current lock pulse to driver and passenger door latches. |
| **B10** | Fuel Tank Flap Motor Close | 1.0 mm² | GN/BK | Electric actuator motor to lock fuel filler door. |
| **B11** | Interior Dome Light Ground Switch | 1.0 mm² | BN/WH | Switched ground control for overhead cabin courtesy lamps. |
| **B12** | Turn Signal Right Output | 1.5 mm² | BK/GN | Direct drive to right exterior turn signal bulbs (hazard alarm flasher). |

---

## 2. Early vs Late Module Interchange Hazards

> [!WARNING]
> **DO NOT DIRECTLY SWAP 996.618.260.xx AND 996.618.262.xx MODULES WITHOUT HARNESS RE-PINNING!**
> 
> The physical 42-pin connector shells are keyed similarly, but pin functions differ drastically:
> 
> 1. **Pin A33 / A12 Pin Conflict (Airbag Crash vs. Electronic Frunk Release):**
>    * On early cars (`260`), **Pin A33 is the Airbag Crash Input** from the Airbag ECU.
>    * On late cars (`262`), **Pin A33 is the Front Trunk Actuator Output**, while the Crash Input was moved to **Pin A12**.
>    * If you plug a late `262` module into an early car without repinning, triggering the front trunk release will send voltage directly into the Airbag ECU crash circuit, or an airbag event could actuate the frunk solenoid!
> 2. **Pin A01 / A22 RF Antenna vs Seat Memory:**
>    * Early units route the coaxial RF antenna lead through Pin A01 and shield ground through Pin A22.
>    * Late units route the Driver Seat Memory digital serial bus through Pin A01 and Targa roof glass switches through Pin A22.
> 3. **Pin A10 / A29 Central Locking Button:**
>    * Early cars use two discrete momentary lines: Pin A10 (Open) and Pin A29 (Close).
>    * Late cars use a single combined toggle input on Pin A29, while Pin A10 drives the sill switch LED.

---

## 3. Immobilizer & Diagnostic Bus Communication

### ACU to DME Serial Handshake (W-Lead)
The immobilizer does **not** authorize engine start over the general CAN bus or OBD diagnostic line. Instead, it utilizes a dedicated bidirectional, single-wire link termed the **W-Lead**:
* **ACU Connector Pin:** `A23` (0.5 mm² Green wire).
* **DME Connector Pin:**
  * **Bosch Motronic ME7.2 (Facelift 2.7L / 3.2L):** Connector IV (40-pin), **Pin 31**.
  * **Bosch Motronic M5.2.2 (Early 2.5L):** Connector III (28-pin), **Pin 31**.

```text
 ┌─────────────────┐                              ┌──────────────────┐
 │  Ignition Lock  │                              │  Bosch ME7.2 DME │
 │   Barrel Coil   │                              │  (Engine Control)│
 └────────┬────────┘                              └─────────▲────────┘
          │ Pins A03/A04                                    │
          │ (Inductive ID48 Read)                           │ Pin IV/31
          ▼                                                 │ (W-Lead Handshake)
 ┌─────────────────┐                              ┌─────────┴────────┐
 │   M534 / M535   │ ─────── Pin A23 (W-Lead) ────│ Serial Challenge │
 │  Immobilizer /  │                              │   & Response     │
 │   Alarm (ACU)   │ ─────── Pin A02 (K-Line) ───▶│ OBD Pin 7 (Diag) │
 └─────────────────┘                              └──────────────────┘
```

**Engine Start Handshake Sequence:**
1. Key inserted into ignition: **Terminal 86S (Pin A16)** goes high (+12V).
2. Key turned to Terminal 15 (Pin A36): ACU energizes the barrel coil (Pins A03/A04) and reads the 32-bit Megamos ID48 transponder pill.
3. ACU compares ID against the 4 enrolled transponder slots in EEPROM (`0x0BA..0x0CD`).
4. If transponder is recognized, ACU exchanges a cryptographic challenge/response with the DME over the **W-Lead (Pin A23)** using the 6-byte paired secret code (`0x1F1..0x1F6`).
5. Upon successful validation, the DME deactivates its software starter lockout and enables fuel injection and ignition spark.

---

## 4. K-Line Diagnostics & Testing Procedures

The ACU diagnostic line is connected to **OBD-II Pin 7**:
* **Connection:** ACU Pin `A02` (0.35 mm² Orange/Black wire) ➔ OBD-II Diagnostic Socket Pin 7.
* **Protocol:** ISO 14230 (KWP2000) Fast Initialization.
* **Target Address:** `0xC0` (Keyword `0x80`, Baud rate 10,400 bps).

### Bench Power-Up Minimum Wiring (for Bench Testing & K-Line Scans)
To power up an M534/M535 module on the bench for diagnostic scanning or EEPROM access:
1. **+12V Power:** Connect `B07` (Terminal 30) and `A36` (Terminal 15) to a clean +12V DC power supply.
2. **Ground:** Connect `B01` (Terminal 31) to Power Supply Negative (GND).
3. **K-Line:** Connect `A02` to Pin 7 of your OBD diagnostic interface (KKL 409.1, Durametric, or PIWIS).
4. **Key In Ignition:** Connect `A16` (Terminal 86S) to +12V.

---

## 5. Fuse & Power Distribution

| Fuse Position | Rating | Circuit Protected |
|:---:|:---:|:---|
| **Fuse C3** | 15A | Alarm Control Unit unswitched main power supply (Terminal 30 to Pin B07). |
| **Fuse D8** | 15A | Central locking motor drive circuit power. |
| **Fuse B8** | 7.5A | Switched ignition power (Terminal 15 to Pin A36). |
| **Fuse E1** | 10A | Terminal 86S key-in-ignition detection. |
| **Internal ACU Fuse** | 15A (Mini-Blade) | Located internally on the ACU circuit board; protects the internal central locking H-bridge motor drivers. |

---

## 6. Water Damage Symptoms & Prevention

Because the module is located in the lowest well of the floorpan under the driver's seat, foam-backed carpet will hold gallons of water from clogged convertible top drainage trays before any moisture is visible on the surface.

### Common Water Ingress Symptoms:
1. **Audible Alarm Siren Triggers Randomly:** Moisture shorts Pin B02 (Alarm Horn) or door contact microswitches to ground.
2. **Power Windows Drop or Cycle Erratically:** Pins A18, A40, or A42 short to battery voltage or ground.
3. **Central Locking Clicks Continuously:** Internal H-bridge motor driver FETs corrode and latch ON.
4. **No-Crank / No-Start Condition:** The internal 93LC66 EEPROM power rail or the W-lead (Pin A23) driver is damaged, preventing transponder authorization.

### Recovery:
1. Disconnect vehicle battery negative terminal immediately.
2. Unbolt driver's seat (4 × E12 Torx bolts) and lift module from floor well.
3. Open module enclosure, submerge PCB in 99% Isopropyl Alcohol (IPA), and scrub gently with a soft nylon brush to remove copper corrosion.
4. If circuit traces or microcontroller pins are eaten through, backup the **93LC66 8-pin EEPROM** and clone it to a matching donor module.
