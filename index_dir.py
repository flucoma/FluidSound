import glob, subprocess, urllib2, json, yaml
from os.path import basename, splitext
import settings

base_url =  "http://localhost:" + str(settings.PORT) + "/similarity/"
audio_dir = "/fluidsound/db/audio/"
yaml_dir = "/fluidsound/db/yaml/"

extractor_path = "essentia_streaming_extractor_freesound"
wav_files = glob.glob(audio_dir + "/*.wav")

index = 0
for w in wav_files:
    print("indexing "+ w)
    yaml_path = yaml_dir+splitext(basename(w))[0]+".yaml"
    command = [extractor_path, w, yaml_path]
    try:
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p_result = p.wait()
        if p_result != 0:
            output_std, output_err = p.communicate()
            print("Essentia extractor returned an error (%s) stdout:%s stderr: %s"%(p_result, output_std, output_err))
            continue
    except Exception as e:
            print("Essentia extractor failed ", e)

    with open(yaml_path, "r+") as f:
        data = yaml.load(f.read())

    inconsistent_descriptors = [
        ("rhythm", "beats_loudness_band_ratio"),
        ("rhythm", "bpm_histogram"),
        ("tonal", "chords_progression"),
        ("tonal", "chords_histogram"),
        ("tonal", "hpcp"),
        ("sfx", "tristimulus"),
        ("sfx", "oddtoevenharmonicenergyratio"),
    ]
    #remove problematic descriptors
    for d in inconsistent_descriptors:
        if d[1] in data[d[0]].keys():
            del data[d[0]][d[1]]
    for k1 in data.keys():
        for k2 in data[k1].keys():
            if type(data[k1][k2]) ==dict and "cov" in data[k1][k2].keys():
                del data[k1][k2]["cov"]
            if type(data[k1][k2]) ==dict and "icov" in data[k1][k2].keys():
                del data[k1][k2]["icov"]

    with open(yaml_path, "w") as f:
        yaml.dump(data,f)

    url = base_url + 'add_point?' + 'sound_id=' + str(index) + '&location=' + str(yaml_path)
    print(url)
    f = urllib2.urlopen(url.replace(" ", "%20"))
    resp = json.loads(f.read())
    if resp["error"]:
        print("Error indexing file")
        print(resp)
        break
    index = index + 1

f = urllib2.urlopen(base_url + "save")
resp = json.loads(f.read())
if resp["error"]:
     print("Error saving index")
else:
    print("done!")
