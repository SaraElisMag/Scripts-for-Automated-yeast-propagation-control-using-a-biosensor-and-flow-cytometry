import FlowCytometryTools as fct
import matplotlib.pyplot as plt
from pylab import *

# Initializes the folder and file used, attributes the data to the 'sample' variable
file_path = r"C:\Users\ADMIN\Desktop\Saras scripts\Data\Goal\2023-08-08_14-00-55\H01.fcs"
sample = fct.FCMeasurement(ID='Test 1', datafile=file_path)

# OBS! The flourochromes listed are factory settings and are needed to call the data from their channels, they do
# not necessarily correspond with the flourochromes used in the sample.
# Data can only be called from the first 'name' (e.g. FITC-A not FL1-A for this setup)

# Event,          Number of events in measurement
# FSC-A,          Forward scatter area -> cell size
# SSC-A,          Side scatter area -> cell granularity
# FITC-A::FL1-A   Green flourochrome
# PE-A::FL2-A,    Orange-Red flourochrome
# PerCP-A::FL3-A, Red flourochrome
# APC-A::FL4-A,   Far-red flourochrome
# FSC-H,          Forward scatter height -> additional size info
# SSC-H,          Side scatter height -> additional granularity info
# FITC-H::FL1-H,  Green intensity at its highest point
# PE-H::FL2-H,    Orange-red intensity at its highest point
# PerCP-H::FL3-H, Red intensity at its highest point
# APC-H::FL4-H,   Far-red intensity at its highest point
# Width,          Pulse width
# Time            Time for recording of each event

# Prints channel names in the sample
# print("Channel names:")
# print(sample.channel_names)

# Transforms the relevant columns from the sample through log, also attributes the number of entities to nmb_ent
# transformed_sample = sample.transform('hlog', channels=['FSC-H', 'SSC-H', 'FITC-H', 'PerCP-H', 'FSC-A', 'SSC-A']
# , b=500.0)
nmb_ent = sample.data.shape[0]

# Initializes the gates based on graphical analysis. Values correspond to corners in a polygon and should be changed
# to fit the particular dataset of interest. The cleanup gate is a threshold for size inclusion.
cleanup_gate_x = fct.ThresholdGate(630000, 'FSC-H', region='above')
cleaned_sample = sample.gate(cleanup_gate_x)
nmb_cells = cleaned_sample.data.shape[0]

debris_gate_x = fct.ThresholdGate(630000, 'FSC-H', region='below')
debris = sample.gate(debris_gate_x)
nmb_debris = debris.data.shape[0]

intact_gate_pos = fct.PolyGate([(1300, 50), (1300, 9000), (400000, 170000), (350000, 50)],
                               ('FITC-H', 'PerCP-H'), region='in', name='Intact Cells OG')

intact_gate_neg = fct.PolyGate([(0, 50), (0, 9000), (1300, 9000), (1300, 50)],
                               ('FITC-H', 'PerCP-H'), region='in', name='Intact Cells OG')

damaged_gate = fct.PolyGate([(0, 9000), (1000, 7e+6), (260000, 8e+6), (400000, 170000), (1300, 9000)],
                            ('FITC-H', 'PerCP-H'), region='in', name='Damaged cells OG')


# - Gates data from the sample and counts number of cells contained in each gate.
# - Calculates the percentage of PI stained cells in the sample (FL3-A).
# - Calculates the mean FL1-H fluorescence for the non-stained cells and GFP positive cells.
# - Prints total number of entities before and after gating, ensures no double counting and inclusion of all entities.
# - Prints total number of cells without debris.
intact_cells_pos = cleaned_sample.gate(intact_gate_pos)
nmb_intact_pos = intact_cells_pos.data.shape[0]

intact_cells_neg = cleaned_sample.gate(intact_gate_neg)
nmb_intact_neg = intact_cells_neg.data.shape[0]

nmb_intact_tot = nmb_intact_neg + nmb_intact_pos

damaged_cells = cleaned_sample.gate(damaged_gate)
nmb_damaged = damaged_cells.data.shape[0]

damaged_percentage = nmb_damaged / nmb_cells * 100

avg_fl1_tot = sum(cleaned_sample['FITC-H']) / nmb_cells
avg_fl1_pos = sum(intact_cells_pos['FITC-H']) / nmb_intact_pos

print("\nNumber of entities total:")
print(nmb_ent)

nmb_ent_gate = nmb_intact_tot + nmb_damaged + nmb_debris
print("\nNumber of entities while gating:")
print(nmb_ent_gate)

nmb_cells_gate = nmb_intact_tot + nmb_damaged
print("\nNumber of cells after gating (no debris):")
print(nmb_cells_gate)

print("\nThe percentage of total cells that are PI positive:")
print(damaged_percentage)

print("\nAverage FL1-H florescence:")
print(avg_fl1_tot)
# print(avg_fl1_pos)

# Plots gated entities in different colors based on previous gating using axes with logarithm scales.
# Also plots legends.
# The first graph plots the cells by GFP and PI, while the second graph plots cells and debris based on
# size and granularity.
fig1 = plt.figure(1)
plt.scatter(cleaned_sample['FITC-H'], cleaned_sample['PerCP-H'], s=0.8, alpha=0.5, label='All Cells')
plt.scatter(damaged_cells.data['FITC-H'], damaged_cells.data['PerCP-H'], s=1.0, alpha=0.5, label='Damaged Cells')
plt.scatter(intact_cells_pos.data['FITC-H'], intact_cells_pos.data['PerCP-H'], s=1.0, alpha=0.5,
            label='Intact (GFP positive)')
plt.scatter(intact_cells_neg.data['FITC-H'], intact_cells_neg.data['PerCP-H'], s=1.0, alpha=0.5,
            label='Intact (GFP negative)')
ax = matplotlib.pyplot.gca()
ax.set_xscale('log')
ax.set_yscale('log')
plt.xlabel('GFP (FL1-H)')
plt.ylabel('PI (FL3-H)')
plt.legend()

fig2 = plt.figure(2)
plt.scatter(sample['FSC-H'], sample['SSC-H'], s=0.8, alpha=0.5, label='All Cells')
plt.scatter(damaged_cells.data['FSC-H'], damaged_cells.data['SSC-H'], s=0.8, alpha=0.5, label='Damaged Cells')
plt.scatter(intact_cells_pos.data['FSC-H'], intact_cells_pos.data['SSC-H'], s=0.8, alpha=0.5,
            label='Intact (GFP Positive)')
plt.scatter(intact_cells_neg.data['FSC-H'], intact_cells_neg.data['SSC-H'], s=0.8, alpha=0.5,
            label='Intact (GFP Negative)')
plt.scatter(debris.data['FSC-H'], debris.data['SSC-H'], s=0.8, alpha=0.8, label='Debris')
ax = matplotlib.pyplot.gca()
ax.set_xscale('log')
ax.set_yscale('log')
plt.xlabel('FSC-H')
plt.ylabel('SSC-H')
plt.legend()

plt.show()
