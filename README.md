## ICD10
A Python library for working with the hierarchy of ICD10 codes. (build top on StefanoTrv/simple_icd_10_CM)

### Overview
ICD10 is a Python library designed to help users explore the structure and details of ICD10 codes. It allows you to retrieve descriptions, hierarchical relationships, and related codes effortlessly.

### Features
- Get detailed information about any ICD10 code, including its description, parent, children, and full parent chain.
- Easy-to-use functions for retrieving and formatting ICD10 data.

### Usage
Here’s a simple example to get you started:

```python
import icd10 as cm

# Format and retrieve detailed data for a specific ICD10 code.
result = cm.get_full_data("S52.112A")
print(result)
```

```json
{
   "code":"S52.112A",
   "description":"Torus fracture of upper end of left radius, initial encounter for closed fracture",
   "type":"extended subcategory",
   "parent":"S52.112",
   "children":[
      
   ],
   "parentChain":{
      "S52.112":{
         "code":"S52.112",
         "description":"Torus fracture of upper end of left radius",
         "type":"subcategory",
         "parent":"S52.11",
         "children":[
            "S52.112A",
            "S52.112D",
            "S52.112G",
            "S52.112K",
            "S52.112P",
            "S52.112S"
         ]
      },
      "S52.11":{
         "code":"S52.11",
         "description":"Torus fracture of upper end of radius",
         "type":"subcategory",
         "parent":"S52.1",
         "children":[
            "S52.111",
            "S52.112",
            "S52.119"
         ],
         "sevenCharacterNote":"The appropriate 7th character is to be added to all codes in subcategory S52.11",
         "sevenCharacterDefinitions":{
            "A":"initial encounter for closed fracture",
            "D":"subsequent encounter for fracture with routine healing",
            "G":"subsequent encounter for fracture with delayed healing",
            "K":"subsequent encounter for fracture with nonunion",
            "P":"subsequent encounter for fracture with malunion",
            "S":"sequela"
         }
      },
      "S52.1":{
         "code":"S52.1",
         "description":"Fracture of upper end of radius",
         "type":"subcategory",
         "parent":"S52",
         "children":[
            "S52.10",
            "S52.11",
            "S52.12",
            "S52.13",
            "S52.18"
         ],
         "excludes2":[
            "physeal fractures of upper end of radius (S59.2-)",
            "fracture of shaft of radius (S52.3-)"
         ],
         "inclusionTerms":[
            "Fracture of proximal end of radius"
         ]
      },
      "S52":{
         "code":"S52",
         "description":"Fracture of forearm",
         "type":"category",
         "parent":"S50-S59",
         "children":[
            "S52.0",
            "S52.1",
            "S52.2",
            "S52.3",
            "S52.5",
            "S52.6",
            "S52.9"
         ],
         "excludes1":[
            "traumatic amputation of forearm (S58.-)"
         ],
         "excludes2":[
            "fracture at wrist and hand level (S62.-)"
         ],
         "sevenCharacterNote":"The appropriate 7th character is to be added to all codes from category S52",
         "sevenCharacterDefinitions":{
            "A":"initial encounter for closed fracture",
            "B":"initial encounter for open fracture type I or II/\tinitial encounter for open fracture NOS",
            "C":"initial encounter for open fracture type IIIA, IIIB, or IIIC",
            "D":"subsequent encounter for closed fracture with routine healing",
            "E":"subsequent encounter for open fracture type I or II with routine healing",
            "F":"subsequent encounter for open fracture type IIIA, IIIB, or IIIC with routine healing",
            "G":"subsequent encounter for closed fracture with delayed healing",
            "H":"subsequent encounter for open fracture type I or II with delayed healing",
            "J":"subsequent encounter for open fracture type IIIA, IIIB, or IIIC with delayed healing",
            "K":"subsequent encounter for closed fracture with nonunion",
            "M":"subsequent encounter for open fracture type I or II with nonunion",
            "N":"subsequent encounter for open fracture type IIIA, IIIB, or IIIC with nonunion",
            "P":"subsequent encounter for closed fracture with malunion",
            "Q":"subsequent encounter for open fracture type I or II with malunion",
            "R":"subsequent encounter for open fracture type IIIA, IIIB, or IIIC with malunion",
            "S":"sequela"
         }
      },
      "S50-S59":{
         "code":"S50-S59",
         "description":"Injuries to the elbow and forearm (S50-S59)",
         "type":"section",
         "parent":"19",
         "children":[
            "S50",
            "S51",
            "S52",
            "S53",
            "S54",
            "S55",
            "S56",
            "S57",
            "S58",
            "S59"
         ],
         "excludes2":[
            "burns and corrosions (T20-T32)",
            "frostbite (T33-T34)",
            "injuries of wrist and hand (S60-S69)",
            "insect bite or sting, venomous (T63.4)"
         ]
      },
      "19":{
         "code":"19",
         "description":"Injury, poisoning and certain other consequences of external causes (S00-T88)",
         "type":"chapter",
         "parent":"",
         "children":[
            "S00-S09",
            "S10-S19",
            "S20-S29",
            "S30-S39",
            "S40-S49",
            "S50-S59",
            "S60-S69",
            "S70-S79",
            "S80-S89",
            "S90-S99",
            "T07-T88",
            "T07",
            "T14",
            "T15-T19",
            "T20-T32",
            "T20-T25",
            "T26-T28",
            "T30-T32",
            "T33-T34",
            "T36-T50",
            "T51-T65",
            "T66-T78",
            "T79",
            "T80-T88"
         ],
         "excludes1":[
            "birth trauma (P10-P15)",
            "obstetric trauma (O70-O71)"
         ],
         "additionalCodes":{
            "use_additional_code":"code to identify any retained foreign body, if applicable (Z18.-)"
         }
      }
   }
}
```

Functions
format_icd10_data(code: str) -> dict
Takes an ICD10 code as input and returns a dictionary containing detailed information about the code, including its description, parent, children, and parent chain.
