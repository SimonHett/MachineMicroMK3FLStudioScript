#---------------------------------------------------------------------------------------------------------
#   NOTES
#---------------------------------------------------------------------------------------------------------
# DON'T CHANGE THIS!
C1 = 0
Cs1 = 1
D1 = 2
Ds1 = 3
E1 = 4
F1 = 5
Fs1 = 6
G1 = 7
Gs1 = 8
A1 = 9
As1 = 10
B1 = 11
C2 = 12
Cs2 = 13
D2 = 14
Ds2 = 15
E2 = 16
F2 = 17
Fs2 = 18
G2 = 19
Gs2 = 20
A2 = 21
As2 = 22
B2 = 23
C3 = 24
Cs3 = 25
D3 = 26
Ds3 = 27
E3 = 28
F3 = 29
Fs3 = 30
G3 = 31
Gs3 = 32
A3 = 33
As3 = 34
B3 = 35
C4 = 36
Cs4 = 37
D4 = 38
Ds4 = 39
E4 = 40
F4 = 41
Fs4 = 42
G4 = 43
Gs4 = 44
A4 = 45
As4 = 46
B4 = 47
C5 = 48
Cs5 = 49
D5 = 50
Ds5 = 51
E5 = 52
F5 = 53
Fs5 = 54
G5 = 55
Gs5 = 56
A5 = 57
As5 = 58
B5 = 59
C6 = 60
Cs6 = 61
D6 = 62
Ds6 = 63
E6 = 64
F6 = 65
Fs6 = 66
G6 = 67
Gs6 = 68
A6 = 69
As6 = 70
B6 = 71
C7 = 72
Cs7 = 73
D7 = 74
Ds7 = 75
E7 = 76
F7 = 77
Fs7 = 78
G7 = 79
Gs7 = 80
A7 = 81
As7 = 82
B7 = 83
C8 = 84
Cs8 = 85
D8 = 86
Ds8 = 87
E8 = 88
F8 = 89
Fs8 = 90
G8 = 91
Gs8 = 92
A8 = 93
As8 = 94
B8 = 95
C9 = 96
Cs9 = 97
D9 = 98
Ds9 = 99
E9 = 100
F9 = 101
Fs9 = 102
G9 = 103
Gs9 = 104
A9 = 105
As9 = 106
B9 = 107
C10 = 108
Cs10 = 109
D10 = 110
Ds10 = 111
E10 = 112
F10 = 113
Fs10 = 114
G10 = 115
Gs10 = 116
A10 = 117
As10 = 118
B10 = 119
C11 = 120
Cs11 = 121
D11 = 122
Ds11 = 123
E11 = 124
F11 = 125
Fs11 = 126
G11 = 127

#---------------------------------------------------------------------------------------------------------
#   CHORD SET 1
#---------------------------------------------------------------------------------------------------------
# CHANGE THE NOTES INSIDE THE BRACKETS AS YOU PLEASE, YOU CAN EVEN ADD MORE THAN 4 NOTES FOR 7TH AND 9TH CHORDS!
# JUST MAKE SURE THERE IS ALWAYS 16 CHORDS IN EACH CHORDSET!

chrd1 = [ # Major 1
    [C3, E4, G4, C5], #1
    [E3, E4, G4, B4],
    [F3, C4, F4, A4],
    [G2, B3, D4, G4],
    [A2, E2, A4, C5], #5
    [E3, E4, A4, B4],
    [G2, D4, A4, B4],
    [D3, D4, F4, A4],
    [F3, G4, A4, C5], #9
    [F3, F4, A4, D5],
    [G3, D4, G4, C5],
    [G2, D4, G4, B4],
    [C3, G4, C5, E5], #13
    [E3, G4, B4, G4],
    [F3, F4, A4, D5],
    [G2, D4, G4, B4],
]

chrd2 = [ # Major 2
    [C3, C4, E4, G4],
    [B2, C4, E4, G4],
    [A2, C4, E4, G4],
    [G2, C4, E4, G4],
    [F2, C4, G4, A4],
    [C3, C4, F4, G4],
    [A2, E4, G4, C5],
    [E3, E4, G4, B4],
    [F2, C4, F4, A4],
    [G2, C4, F4, A4],
    [G2, C4, D4, G4],
    [G2, B3, E4, G4],
    [C3, E4, A4, C5],
    [B2, C4, E4, A4],
    [D3, G4, B4, D5],
    [C3, E4, G4, C5],
]

chrd3 = [ # Minor 1
    [C3, C4, Ds4, G4],
    [Ds3, C4, Ds4, G4],
    [F3, C4, F4, Gs4],
    [G2, B3, D4, G4],
    [Gs2, C4, Ds4, G4],
    [Ds3, As3, Ds4, G4],
    [G2, As3, D4, G4],
    [As2, As3, D4, F4],
    [F2, A3, C4, F4],
    [Gs2, C4, F4, Gs4],
    [G2, C4, Ds4, G4],
    [G2, B3, D4, G4],
    [C3, Ds4, C4, Ds5],
    [G2, As3, Ds4, G4],
    [Gs2, C4, F4, Gs4],
    [G2, C4, Ds4, G4],
]

chrd4 = [ # Minor 2
    [C3, G3, C4, Ds4],
    [B2, G3, B3, Ds4],
    [As2, G3, C4, Ds4],
    [A2, C4, Ds4, G4],
    [Gs2, C4, Ds4, G4],
    [Ds3, As3, D4, G4],
    [F2, C4, F4, Gs4],
    [As2, D4, F4, Gs4],
    [C3, C4, Ds4, G4],
    [As2, C4, D4, F4],
    [Gs2, As3, C4, Ds4],
    [G2, C4, D4, F4],
    [C3, As3, Ds4, G4],
    [Ds3, C4, Ds4, As4],
    [F3, Ds4, G4, C5],
    [D3, D4, F4, As4],
]

maj1 = [
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
]

maj2 = [
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
]

maj3 = [
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
]

maj4 = [
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
    [C4, C5, E5, G5],
]

# DON'T CHANGE THIS!
chdSet = [chrd1, chrd2, chrd3, chrd4, maj1, maj2, maj3, maj4]

#---------------------------------------------------------------------------------------------------------
#   GROUPS
#---------------------------------------------------------------------------------------------------------
# CHANGE THE NOTES INSIDE THE BRACKETS AS YOU PLEASE, JUST MAKE SURE THAT THERE IS EXACTLY 16 NOTES IN EACH GROUP!

group1 = [C5, D5, E5, F5, G5, A5, B5, C6, D6, E6, F6, G6, A6, B6, C7, D7]       # MAJOR
group2 = [C5, D5, Ds5, F5, G5, Gs5, As5, C6, D6, Ds6, F6, G6, Gs6, As6, C7, D7] # MINOR
group3 = [C5, Cs5, D5, Ds5, E5, F5, Fs5, G5, Gs5, A5, As5, B5, C6, Cs6, D6, Ds6]# CHROMATIC
group4 = [C5, Cs5, E5, F5, G5, Gs5, B5, C6, Cs6, E6, F6, G6, Gs6, B6, C7, Cs7]# ARABIC
group5 = [Cs4, C4, Fs4, As4, E4, D4, As4, Gs4, C5, B4, A4, G4, Cs5, G5, Ds5, F5]# FPC
group6 = [C5, Cs5, D5, Ds5, E5, F5, Fs5, G5, Gs5, A5, As5, B5, C6, Cs6, D6, Ds6]# CUSTOM
group7 = [C5, Cs5, D5, Ds5, E5, F5, Fs5, G5, Gs5, A5, As5, B5, C6, Cs6, D6, Ds6]# CUSTOM
group8 = [C4, D4, Gs4, As4, Cs4, E4, A4, F4, B4, Fs4, Ds4, G4, C5, Cs5, D5, G5] # BATTERY

# DON'T CHANGE THIS!
groups = [group1, group2, group3, group4, group5, group6, group7, group8]