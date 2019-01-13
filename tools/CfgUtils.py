import glob

def readSamplesConfig(configFileName):
    
    # read sample configuration file

    samples = {}
    cfg_data = ""
    
    with open(configFileName, 'r') as f:
        cfg_data = f.read()

    # check for imports
    for line in cfg_data.split("\n"):
        if "#import" in line:
            with open(line.split("import")[-1].strip(), 'r') as f:
                cfg_data_import = f.read()
                cfg_data = cfg_data_import + cfg_data
    
    shortname = ""
    xsec = 0.0
    lumi = 0.0
    signalscalingfactor = 0.0
    filtereff = -1
    plot = False
    color = -1
    descriptor = ""
    sampletype = ""
    
    for line in cfg_data.split("\n"):
       
        if len(line)>0 and line[0] == "#":
            continue
       
        try:
            if "[" in line and "]" in line:
                shortname = line.split("[")[1].split("]")[0]
                samples[shortname] = {}
            if "xsec" in line:
                xsec = line.split("=")[-1].strip()
                samples[shortname]["xsec"] = float(xsec)
            if "lumi" in line:
                lumi = line.split("=")[-1].strip()
                samples[shortname]["lumi"] = float(lumi)
            if "signalscalingfactor" in line:
                signalscalingfactor = line.split("=")[-1].strip()
                samples[shortname]["signalscalingfactor"] = float(signalscalingfactor)
            if "filtereff" in line:
                filtereff = line.split("=")[-1].strip()
                samples[shortname]["filtereff"] = float(filtereff)
            if "plot" in line:
                plot = line.split("=")[-1].strip()
                samples[shortname]["plot"] = eval(plot)
            if "descriptor" in line:
                descriptor = line.split("=")[-1].strip()
                samples[shortname]["descriptor"] = descriptor
            if "type" in line:
                sampletype = line.split("=")[-1].strip()
                samples[shortname]["type"] = sampletype
            if "color" in line:
                color = line.split("=")[-1].strip()
                samples[shortname]["color"] = int(color)

        except:
            print "[!] malformed sample configuration file!"

    return samples


def update_samples_with_filenames(tree_folder, configuration_file):

    samples = readSamplesConfig(configuration_file)

    for file_name in glob.glob(tree_folder + "/*.root"):

        for sample in samples:

            sample_name = sample.replace("_RA2AnalysisTree", "")

            if "filenames" not in samples[sample]:
                samples[sample]["filenames"] = []
            if sample_name in file_name:
                samples[sample]["filenames"].append(file_name)
                break

    for sample in samples.keys():
        if sample != "global":
            if "filenames" not in samples[sample]:
                del samples[sample]
            elif len(samples[sample]["filenames"]) == 0:
                del samples[sample]
    return samples
