'''<b>Dynamic Classify Objects</b> classifies objects into different
classes according to the value of measurements you choose. This
modification allows these measurements to change for each image in an
imageset.

<hr>
This module classifies objects into a number of different bins according
to the value of a measurement (e.g., by size, intensity, shape).  It
reports how many objects fall into each class as well as the percentage
of objects that fall into each class. The module asks you to select the
measurement feature to be used to classify your objects and specify the
bins to use. It also requires you to have run a measurement or
<b>CalculateMath</b> previous to this module in the pipeline so that the
measurement values can be used to classify the objects.

<p>Each object is classified according to the measurements you choose
and assigns each object to one class per measurement. You may specify
more than two classification bins per measurement.</p>

<p>Note that objects without a measurement are not counted as belonging
in a classification bin and will not show up in the output image (shown
in the module display window); in the object classification they will
have a value of False for all bins. However, they are still counted in
the total number of objects and hence are reflected in the
classification percentages.</p>

<h4>Available measurements</h4>
<ul>
<li><b>Image measurements:</b>
<ul>
<li><i>NumObjectsPerBin:</i> The number of objects that are classified
into each bin.</li>
<li><i>PctObjectsPerBin:</i> The percentage of total objects that are
classified into each bin.</li>
</ul>
</li>
<li><b>Object measurements:</b>
Single measurement: Classification (true/false) of the N<sup>th</sup>
bin for the M<sup>th</sup> measurement.
</li>
</ul>

See also <b>CalculateMath</b> and any of the modules in the
<b>Measure</b> category.
'''

# This module is distributed under the GNU General Public License.
# See the accompanying file LICENSE for details.
#
# Copyright (c) 2003-2009 Massachusetts Institute of Technology
# Copyright (c) 2009-2014 Broad Institute
# Copyright (c) 2014 Edward J. Stronge
#
# Cell Profiler website: http://www.cellprofiler.org


import cellprofiler.preferences as cpprefs

import numpy as np

import cellprofiler.cpmodule as cpm
import cellprofiler.measurements as cpmeas
import cellprofiler.cpimage as cpi
import cellprofiler.settings as cps
from cellprofiler.settings import YES, NO


BC_EVEN = "Evenly spaced bins"
BC_CUSTOM = "Custom-defined bins"

M_CATEGORY = "Classify"
F_PCT_PER_BIN = 'PctObjectsPerBin'
F_NUM_PER_BIN = 'NumObjectsPerBin'


class ClassifyObjects(cpm.CPModule):
    category = "Object Processing"
    module_name = "DynamicClassifyObjects"
    variable_revision_number = 1

    def create_settings(self):
        """Create the settings for the module

        Create the settings for the module during initialization.
        """

        # A list holding groupings for each of the single measurements
        # to be done
        self.single_measurements = []

        # A count of # of measurements
        self.single_measurement_count = cps.HiddenCount(
            self.single_measurements)

        # Add one single measurement to start off
        self.add_single_measurement(False)

        # A button to press to get another measurement
        self.add_measurement_button = cps.DoSomething(
            "", "Add another classification", self.add_single_measurement)

    def add_single_measurement(self, can_delete=True):
        '''Add a single measurement to the group of single measurements

        can_delete - True to include a "remove" button, False if you're not
                     allowed to remove it.
        '''
        group = cps.SettingsGroup()
        if can_delete:
            group.append("divider", cps.Divider(line=True))

        group.append("object_name", cps.ObjectNameSubscriber(
            "Select the object to be classified", cps.NONE,
            doc="""The name of the objects to be classified. You can
            choose from objects created by any previous module. See
            <b>IdentifyPrimaryObjects</b>, <b>IdentifySecondaryObjects</b>, or
            <b>IdentifyTertiaryObjects</b>."""))

        def object_fn():
            return group.object_name.value
        group.append("measurement", cps.Measurement(
            "Select the measurement to classify by", object_fn, doc="""
            Select a measurement made by a previous module. The objects
            will be classified according to their values for this
            measurement."""))

        group.append("bin_choice", cps.Choice(
            "Select bin spacing",
            [BC_EVEN, BC_CUSTOM], doc="""
            You can either specify bins of equal size, bounded by
            upper and lower limits, or you can specify custom values that
            define the edges of each bin with a threshold.

            <i>Note:</i> If you would like two bins, choose
            <i>Custom-defined bins</i> and then provide a single
            threshold when asked.
            <i>Evenly spaced bins</i> creates the indicated number of bins
            at evenly spaced intervals between the low and high threshold.
            You also have the option to create bins for objects that fall below
            or above the low and high threhsold"""))

        group.append("bin_count", cps.Integer(
            "Number of bins", 3, minval=1, doc="""
            This is the number of bins that will be created between
            the low and high threshold"""
        ))

        group.append("wants_image_based_low_threshold", cps.Binary(
            "Use an image measurement as a low threshold", True, doc="""
            Select <i>%(YES)s</i> to set a threshold using a parameter
            from the image associated with the selected objects.
            <p>Select <i>%(NO)s</i> to specify a single threshold value
            that will be used for each image.""" % globals()))

        group.append("top_threshold_divider", cps.Divider(line=True))

        def object_fn():
            return cpmeas.IMAGE
        group.append('low_threshold_measurement', cps.Measurement(
            "Measurement to use for low threshold", object_fn, doc="""
            Choose the measurement to use in determining the low
            threshold value. This must be a measurement made by some
            previous module on the whole image."""))

        group.append("low_threshold", cps.Float(
            "Lower threshold", 0, doc="""
            <i>(Used only if Evenly spaced bins selected)</i><br> This
            is the threshold that separates the lowest bin from the
            others. The lower threshold, upper threshold, and number of
            bins define the thresholds of bins between the lowest and
            highest."""))

        group.append("wants_low_bin", cps.Binary(
            "Use a bin for objects below the threshold?", False, doc="""
            Select <i>%(YES)s</i> if you want to create a bin for objects
            whose values fall below the low threshold. Select <i>%(NO)s</i>
            if you do not want a bin for these objects.""" % globals()))

        def min_upper_threshold():
            return group.low_threshold.value + np.finfo(float).eps

        group.append("middle_threshold_divider", cps.Divider(line=True))

        group.append("wants_image_based_high_threshold", cps.Binary(
            "Use an image measurement as a high threshold", False, doc="""
            Select <i>%(YES)s</i> to set a threshold using a parameter
            from the image associated with the selected objects.
            <p>Select <i>%(NO)s</i> to specify a single threshold value
            that will be used for each image.""" % globals()))

        def object_fn():
            return cpmeas.IMAGE
        group.append('high_threshold_measurement', cps.Measurement(
            "Measurement to use for high threshold", object_fn, doc="""
            Choose the measurement to use in determining the high
            threshold value. This must be a measurement made by some
            previous module on the whole image."""))

        group.append("high_threshold", cps.Float(
            "Upper threshold", 1,
            minval=cps.NumberConnector(min_upper_threshold), doc="""
            <i>(Used only if Evenly spaced bins selected)</i><br> This
            is the threshold that separates the last bin from the
            others. <i>Note:</i> If you would like two bins, choose
            <i>Custom-defined bins</i>."""))

        group.append("wants_high_bin", cps.Binary(
            "Use a bin for objects above the threshold?", False, doc="""
            Select <i>%(YES)s</i> if you want to create a bin for
            objects whose values are above the high threshold. <br>
            Select <i>%(NO)s</i> if you do not want a bin for these
            objects.""" % globals()))

        group.append("bottom_threshold_divider", cps.Divider(line=True))

        group.append("custom_thresholds", cps.Text(
            "Enter the custom thresholds separating the values between bins",
            "0,1", doc="""
            <i>(Used only if Custom thresholds selected)</i><br> This
            setting establishes the threshold values for the bins. You
            should enter one threshold between each bin, separating
            thresholds with commas (for example, <i>0.3, 1.5, 2.1</i>
            for four bins). The module will create one more bin than
            there are thresholds."""))

        group.append("wants_custom_names", cps.Binary(
            "Give each bin a name?", False, doc="""
            Select <i>%(YES)s</i> to assign custom names to bins you
            have specified. <p>Select <i>%(NO)s</i> for the module to
            automatically assign names based on the measurements and the
            bin number.""" % globals()))

        group.append("bin_names", cps.Text(
            "Enter the bin names separated by commas", cps.NONE, doc="""
            <i>(Used only if Give each bin a name? is checked)</i><br>
            Enter names for each of the bins, separated by commas. An
            example including three bins might be <i>First, Second,
            Third</i>."""))

        group.append("wants_images", cps.Binary(
            "Retain an image of the classified objects?", False, doc="""
            Select <i>%(YES)s</i> to keep an image of the objects which
            is color-coded according to their classification, for use
            later in the pipeline (for example, to be saved by a
            <b>SaveImages</b> module).""" % globals()))

        group.append("image_name", cps.ImageNameProvider(
            "Name the output image", "ClassifiedNuclei", doc="""
            Enter the name to be given to the classified object
            image."""))

        group.can_delete = can_delete

        def number_of_bins():
            '''Return the # of bins in this classification'''
            if group.bin_choice == BC_EVEN:
                value = group.bin_count.value
            else:
                value = len(group.custom_thresholds.value.split(","))-1
            if group.wants_low_bin:
                value += 1
            if group.wants_high_bin:
                value += 1
            return value
        group.number_of_bins = number_of_bins

        def measurement_name():
            '''Get the measurement name to use inside the bin name

            Account for conflicts with previous measurements
            '''
            measurement_name = group.measurement.value
            other_same = 0
            for other in self.single_measurements:
                if id(other) == id(group):
                    break
                if other.measurement.value == measurement_name:
                    other_same += 1
            if other_same > 0:
                measurement_name += str(other_same)
            return measurement_name

        def bin_feature_names():
            '''Return the feature names for each bin'''
            if group.wants_custom_names:
                return [name.strip()
                        for name in group.bin_names.value.split(",")]
            return ['_'.join((measurement_name(),
                              'Bin_%d' % (i+1)))
                    for i in range(number_of_bins())]
        group.bin_feature_names = bin_feature_names

        def validate_group():
            bin_name_count = len(bin_feature_names())
            bin_count = number_of_bins()
            if bin_count < 1:
                bad_setting = (group.bin_count if group.bin_choice == BC_EVEN
                               else group.custom_thresholds)
                raise cps.ValidationError(
                    """You must have at least one bin in order to take
                    measurements.  Either add more bins or ask for bins
                    for objects above or below threshold""",
                    bad_setting)
            if bin_name_count != number_of_bins():
                raise cps.ValidationError(
                    "The number of bin names (%d) does not match the"
                    "number of bins (%d)." %
                    (bin_name_count, bin_count), group.bin_names)
            for bin_feature_name in bin_feature_names():
                cps.AlphanumericText.validate_alphanumeric_text(
                    bin_feature_name, group.bin_names, True)
            if group.bin_choice == BC_CUSTOM:
                try:
                    [float(x.strip())
                     for x in group.custom_thresholds.value.split(",")]
                except ValueError:
                    raise cps.ValidationError(
                        'Custom thresholds must be a comma-separated list '
                        'of numbers (example: "1.0, 2.3, 4.5")',
                        group.custom_thresholds)
        group.validate_group = validate_group

        if can_delete:
            group.remove_settings_button = cps.RemoveSettingButton(
                "", "Remove the above classification",
                self.single_measurements, group)
        self.single_measurements.append(group)

    def settings(self):
        result = [self.single_measurement_count]
        result += reduce(lambda x, y: x+y,
                         [group.pipeline_settings()
                          for group in self.single_measurements])
        return result

    def visible_settings(self):

        result = []
        for group in self.single_measurements:
            if group.can_delete:
                result += [group.divider]
            result += [group.object_name, group.measurement,
                       group.bin_choice]
            if group.bin_choice == BC_EVEN:
                result += [group.bin_count, group.top_threshold_divider]
                for dynamic_threshold, measurement, \
                    static_threshold, extra_bin in (
                        (group.wants_image_based_low_threshold,
                            group.low_threshold_measurement,
                            group.low_threshold, group.wants_low_bin),
                        (group.wants_image_based_high_threshold,
                            group.high_threshold_measurement,
                            group.high_threshold, group.wants_high_bin)):
                    result += [dynamic_threshold]
                    if not dynamic_threshold:
                        result += [static_threshold, extra_bin]
                    else:
                        result += [measurement]
                    if group.middle_threshold_divider not in result:
                        result += [group.middle_threshold_divider]
            else:
                result += [group.custom_thresholds,
                           group.wants_low_bin, group.wants_high_bin]
            result += [group.bottom_threshold_divider]
            result += [group.wants_custom_names]
            if group.wants_custom_names:
                result += [group.bin_names]
            result += [group.wants_images]
            if group.wants_images:
                result += [group.image_name]
            if group.can_delete:
                result += [group.remove_settings_button]
        result += [self.add_measurement_button]
        return result

    def run(self, workspace):
        """Classify the objects in the image cycle"""
        if self.show_window:
            workspace.display_data.labels = []
            workspace.display_data.bins = []
            workspace.display_data.values = []
        for group in self.single_measurements:
            self.run_single_measurement(group, workspace)

    def display(self, workspace, figure):
        self.display_single_measurement(workspace, figure)

    def run_single_measurement(self, group, workspace):
        '''Classify objects based on one measurement'''
        object_name = group.object_name.value
        feature = group.measurement.value
        objects = workspace.object_set.get_objects(object_name)
        measurements = workspace.measurements
        values = measurements.get_current_measurement(object_name, feature)
        if group.bin_choice == BC_EVEN:

            if group.wants_image_based_low_threshold:
                low_threshold = measurements.get_current_image_measurement(
                    group.low_threshold_measurement.value)
            else:
                low_threshold = group.low_threshold.value

            if group.wants_image_based_high_threshold:
                high_threshold = measurements.get_current_image_measurement(
                    group.high_threshold_measurement.value)
            else:
                high_threshold = group.high_threshold.value

            bin_count = group.bin_count.value
            thresholds = (np.arange(bin_count+1) *
                          (high_threshold - low_threshold)/float(bin_count) +
                          low_threshold)
        else:
            thresholds = [float(x.strip())
                          for x in group.custom_thresholds.value.split(', ')]
        #
        # Put infinities at either end of the thresholds so we can bin the
        # low and high bins
        #
        thresholds = np.hstack(([-np.inf] if group.wants_low_bin else [],
                                thresholds,
                                [np.inf] if group.wants_high_bin else []))
        #
        # Do a cross-product of objects and threshold comparisons
        #
        ob_idx, th_idx = np.mgrid[0:len(values), 0:len(thresholds)-1]
        bin_hits = ((values[ob_idx] > thresholds[th_idx]) &
                    (values[ob_idx] <= thresholds[th_idx+1]))
        num_values = len(values)
        for bin_idx, feature_name in enumerate(group.bin_feature_names()):
            measurement_name = '_'.join((M_CATEGORY, feature_name))
            measurements.add_measurement(object_name, measurement_name,
                                         bin_hits[:, bin_idx].astype(int))
            measurement_name = '_'.join(
                (M_CATEGORY, feature_name, F_NUM_PER_BIN))
            num_hits = bin_hits[:, bin_idx].sum()
            measurements.add_measurement(cpmeas.IMAGE, measurement_name,
                                         num_hits)
            measurement_name = '_'.join(
                (M_CATEGORY, feature_name, F_PCT_PER_BIN))
            measurements.add_measurement(
                cpmeas.IMAGE, measurement_name,
                100.0*float(num_hits)/num_values if num_values > 0 else 0)
        if group.wants_images or (self.show_window):
            colors = self.get_colors(bin_hits.shape[1])
            object_bins = np.sum(bin_hits * th_idx, 1)+1
            object_color = np.hstack(([0], object_bins))
            object_color[np.hstack((False, np.isnan(values)))] = 0
            labels = object_color[objects.segmented]
            if group.wants_images:
                image = colors[labels, :3]
                workspace.image_set.add(
                    group.image_name.value,
                    cpi.Image(image, parent_image=objects.parent_image))

            if self.show_window:
                workspace.display_data.bins.append(object_bins[~np.isnan(values)])
                workspace.display_data.labels.append(labels)
                workspace.display_data.values.append(values[~np.isnan(values)])

    def display_single_measurement(self, workspace, figure):
        '''Display an array of single measurements'''
        figure.set_subplots((3, len(self.single_measurements)))
        for i, group in enumerate(self.single_measurements):
            bin_hits = workspace.display_data.bins[i]
            labels = workspace.display_data.labels[i]
            values = workspace.display_data.values[i]
            if len(values) == 0:
                continue
            #
            # A histogram of the values
            #
            axes = figure.subplot(0, i)
            axes.hist(values[~np.isnan(values)])
            axes.set_xlabel(group.measurement.value)
            axes.set_ylabel("# of %s" % group.object_name.value)
            #
            # A histogram of the labels yielding the bins
            #
            axes = figure.subplot(1, i)
            axes.hist(bin_hits, bins=group.number_of_bins(),
                      range=(.5, group.number_of_bins()+.5))
            axes.set_xticks(np.arange(1, group.number_of_bins()+1))
            if group.wants_custom_names:
                axes.set_xticklabels(group.bin_names.value.split(","))
            axes.set_xlabel(group.measurement.value)
            axes.set_ylabel("# of %s" % group.object_name.value)
            colors = self.get_colors(len(axes.patches))
            for j, patch in enumerate(axes.patches):
                patch.set_facecolor(colors[j+1, :])
            #
            # The labels matrix
            #
            figure.subplot_imshow_labels(2, i, labels,
                                         title=group.object_name.value,
                                         renumber=False,
                                         sharexy=figure.subplot(2, 0))

    def get_colors(self, count):
        '''Get colors used for two-measurement labels image'''
        import matplotlib.cm as cm
        cmap = cm.get_cmap(cpprefs.get_default_colormap())
        #
        # Trick the colormap into divulging the values used.
        #
        sm = cm.ScalarMappable(cmap=cmap)
        colors = sm.to_rgba(np.arange(count)+1)
        return np.vstack((np.zeros(colors.shape[1]), colors))

    def prepare_settings(self, setting_values):
        """Do any sort of adjustment to the settings required for the
        given values

        setting_values - the values for the settings. See the
            ClassifyObjects.settings() function

        This method allows a module to specialize itself according to
        the number of settings and their value. For instance, a module
        that takes a variable number of images or objects can increase
        or decrease the number of relevant settings so they map
        correctly to the values."""

        single_measurement_count = int(setting_values[0])
        if single_measurement_count < len(self.single_measurements):
            del self.single_measurements[single_measurement_count:]
        while single_measurement_count > len(self.single_measurements):
            self.add_single_measurement(True)

    def validate_module(self, pipeline):
        for group in self.single_measurements:
            group.validate_group()

    def upgrade_settings(self, setting_values, variable_revision_number,
                         module_name, from_matlab):
        '''Adjust setting values if they came from a previous revision

        setting_values - a sequence of strings representing the settings
                         for the module as stored in the pipeline
        variable_revision_number - the variable revision number of the
                         module at the time the pipeline was saved. Use this
                         to determine how the incoming setting values map
                         to those of the current module version.
        module_name - the name of the module that did the saving. This can be
                      used to import the settings from another module if
                      that module was merged into the current module
        from_matlab - True if the settings came from a Matlab pipeline, False
                      if the settings are from a CellProfiler 2.0 pipeline.

        Overriding modules should return a tuple of setting_values,
        variable_revision_number and True if upgraded to CP 2.0, otherwise
        they should leave things as-is so that the caller can report
        an error.
        '''
        return setting_values, variable_revision_number, from_matlab

    def get_measurement_columns(self, pipeline):
        columns = []
        for group in self.single_measurements:
            columns += [(cpmeas.IMAGE,
                         '_'.join((M_CATEGORY, feature_name, F_NUM_PER_BIN)),
                         cpmeas.COLTYPE_INTEGER)
                        for feature_name in group.bin_feature_names()]
            columns += [(cpmeas.IMAGE,
                         '_'.join((M_CATEGORY, feature_name, F_PCT_PER_BIN)),
                         cpmeas.COLTYPE_FLOAT)
                        for feature_name in group.bin_feature_names()]
            columns += [(group.object_name.value,
                         '_'.join((M_CATEGORY, feature_name)),
                         cpmeas.COLTYPE_INTEGER)
                        for feature_name in group.bin_feature_names()]
        return columns

    def get_categories(self, pipeline, object_name):
        """Return the categories of measurements that this module
        produces

        object_name - return measurements made on this object (or
        'Image' for image measurements)
        """
        if ((object_name == cpmeas.IMAGE) or
            (object_name in [group.object_name.value
                             for group in self.single_measurements])):
            return [M_CATEGORY]

        return []

    def get_measurements(self, pipeline, object_name, category):
        """Return the measurements that this module produces

        object_name - return measurements made on this object (or
            'Image' for image measurements)
        category - return measurements made in this category
        """
        if category != M_CATEGORY:
            return []
        result = []
        for group in self.single_measurements:
            if group.object_name == object_name:
                return group.bin_feature_names()
            elif object_name == cpmeas.IMAGE:
                for image_features in (F_NUM_PER_BIN, F_PCT_PER_BIN):
                    for bin_feature_names in group.bin_feature_names():
                        result += [
                            '_'.join((bin_feature_names, image_features))]
                return result
        return []
