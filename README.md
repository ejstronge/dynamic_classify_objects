

# Classify Objects, with image-based thresholds

# Edward J. Stronge <ejstronge@gmail.com>

Modifications to the excellent `Cell Profiler` module `classifyobjects` to allow
per-cycle threshold settings.

# Using this module

## Installation

Either download `dynamicclassifyobjects.py` directly or clone this repository.
In either case, you'll need to move `dynamicclassifyobjects.py` to your
CellProfiler plugins directory. 
*See below for directions on how to find your plugins directory.*

### Locating your CellProfiler plugins directory

To find the plugins directory, open up Cell Profiler and navigate to
File > Preferences and locate the "CellProfiler plugins directory" options.
You may need to create this directory if it doesn't exist.

## Usage

Use the CellProfiler graphical user interface as you normally would. This
module documents its settings in the same way an official CellProfiler module
would.

# Why this module?


## The problem

<p align="center">
<img src="https://github.com/ejstronge/ /tests/input_images/large_img.png"></img>
<img src="https://github.com/ejstronge/ /tests/input_images/small_img.png"></img>
</p>

<p align="center">
<img src="https://github.com/ejstronge/ /tests/classification_output/large_img_static.png"></img>
<img src="https://github.com/ejstronge/ /tests/classification_output/small_img_static.png"></img>
</p>

<p align="center">
<img src="https://github.com/ejstronge/ /tests/classification_output/large_img_dynamic.png"></img>
<img src="https://github.com/ejstronge/ /tests/classification_output/small_img_dynamic.png"></img>
</p>

## A solution

* general overview of approach

* link to CP developer pages
* mention trunk build tutorial folder

(c) 2014, Edward J. Stronge. Released under the GPLv2 - see LICENSE for 
details.
