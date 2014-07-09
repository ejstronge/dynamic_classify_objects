

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

The CellProfiler `classifyobjects` module takes previously identified objects
and employs criteria specified by a user to group the objects. The grouping
requires a high and a low threshold parameter.

If one wanted to classify the objects identified in a large number of images
by their *y* coordinate, it would be necessary to either:

* Ensure that all the images have the same height: This is possible for images
  acquired from a single microscope. However, if expert image processing is
  required (e.g., producing crops that only target a specific region of a
  coronal brain slice) image parameters could vary.

* Process images with similar heights in separate batches: This is a possibility
  but is tedious and would yield imprecise results.

The main issue is that there's no way to ask the module to automatically choose
a threshold value based on the image in which an object was identified.


### An example

Consider this toy example of a single image and a version of the image
with its height reduced 50%. Colors indicate membership in the clusters that
CellProfiler's `classifyobjects` module has identified:

<img src="https://github.com/ejstronge/dyamic_classify_objects/raw/master/tests/classification_output/large_img_static.png" ></img>

<img src="https://github.com/ejstronge/dyamic_classify_objects/raw/master/tests/classification_output/small_img_static.png" ></img>

There are only two groups identified in the small image because the analysis
pipeline used the same threshold value for both images. You can play with
this example by using the .cpproj files in the `tests` directory.

### Using dynamicclassifyobjects

Luckily, the excellent CellProfiler documentation made it easy to adapt
the `classifyobjects` module to choose threshold values based on each
analyzed image.

Here is an analysis of the same toy example. Now, the group classifications
are similar in both the original and reduced images:

<img src="https://github.com/ejstronge/dyamic_classify_objects/raw/master/tests/classification_output/large_img_dynamic.png" ></img>

<img src="https://github.com/ejstronge/dyamic_classify_objects/raw/master/tests/classification_output/small_img_dynamic.png" ></img>


## Links to useful resources for CellProfiler development

Thanks again to the great resources available online, writing this module
was reasonably straightforward. The following are sites I found useful:


* Check out the [development build of CellProfiler](https://github.com/CellProfiler/CellProfiler/) for multiple code samples.
  Look in the `tutorial` folder for introductory examples.

* [Information about the architecture of CellProfiler](https://github.com/CellProfiler/CellProfiler/wiki/Module-Structure-and-Data-Storage-Retrieval)

* [Templates for starting a new module](https://github.com/CellProfiler/CellProfiler/wiki/Writing-a-CellProfiler-module#module-templates)

(c) 2014, Edward J. Stronge. Released under the GPLv2 - see LICENSE for details.
