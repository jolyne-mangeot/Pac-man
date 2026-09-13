var normal_mode = {
 "base" :   { "page": "race-human-base-dark", "column": 3, "row": 0,
              "hands": { "left":  { "column": 0, "row": 17 },
                         "right": { "column": 0, "row": 18 }
                       },
              "whands": "race-human-weapon-hands-dark"
            },
 "clothes": { "page": "clothes-2", "column": 1, "row": 2 }, // clothes 2, gray robe
 "beard":   "none", // none
 "hat":     { "page": "clothes-2", "column": 2, "row": 0 }, // gray hood
 "weapon" : "none",
 "shield" : "none"
};

var super_mode = {
 "base" :   { "page": "race-human-base-dark", "column": 3, "row": 0,
              "hands": { "left":  { "column": 0, "row": 17 },
                         "right": { "column": 0, "row": 18 }
                       },
              "whands": "race-human-weapon-hands-dark"
            },
 "clothes": { "page": "clothes-2", "column": 1, "row": 2 }, // clothes 2, gray robe
 "beard":   "none", // none
 "hat":     { "page": "clothes-2", "column": 2, "row": 0 }, // gray hood
 "weapon" : { "material": "2", "column": 1, "row": 0 },
 "shield" : "none"
};

// Select the one to be drawn
var g_char = super_mode;
