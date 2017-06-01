import copy
import os

import json
import numpy as np
import scipy.io.wavfile

from cultures.makam import utilities, svgparser


DOCS_PATH = os.path.join(os.path.dirname(__file__), '..', 'scores')


def read_raw_audio(audio_path):
    rate, data = scipy.io.wavfile.read(audio_path)

    len_audio = np.size(data)
    min_audio = np.min(data)
    max_audio = np.min(data)
    return data, len_audio, min_audio, max_audio


def load_pitch(pitch_path):
    pitch_data = json.load(open(pitch_path))
    pp = np.array(pitch_data['pitch'])

    time_stamps = pp[:, 0]
    pitch_curve = pp[:, 1]
    pitch_plot = copy.copy(pitch_curve)
    pitch_plot[pitch_plot < 20] = np.nan

    samplerate = pitch_data['sampleRate']
    hopsize = pitch_data['hopSize']

    max_pitch = np.max(pitch_curve)
    min_pitch = np.min(pitch_curve)

    return time_stamps, pitch_plot, max_pitch, min_pitch, samplerate, hopsize


def load_pd(pd_path):
    pd = json.load(open(pd_path))
    vals = pd["vals"]
    bins = pd["bins"]
    return vals, bins


def load_tonic(tonic_path):
    tnc = json.load(open(tonic_path))
    try:
        return [tnc['value']]
    except KeyError:
        return [work['value'] for work in tnc.values()]


def get_feature_paths(recid):
    FEATURES =  ['melodic_progression', 'metadata', 'note_models', 'pitch'
                 'pitch_distribution', 'pitch_filtered', 'tonic', 'notes',
                 'sections']

    doc_folder = os.path.join(DOCS_PATH, recid)
    (full_names, folders, names) = \
        utilities.get_filenames_in_dir(dir_name=doc_folder, keyword='*.json')

    paths = {'audio_path_mp3': os.path.join(doc_folder, recid + '.mp3'),
             'audio_path_wav': os.path.join(doc_folder, recid + '.wav')}

    for xx, name in enumerate(names):
        if name.split('.json')[0].split('--')[1] in FEATURES:
            paths[name.split('.json')[0]] = full_names[xx]
    return paths


def load_notes(notes_path):
    notes = json.load(open(notes_path))
    return notes


def get_sections(sections_path):
    sections_dict = json.load(open(sections_path))
    metadata_path = sections_path.split('jointanalysis--sections.json')[0] + \
                    'audioanalysis--metadata.json'

    metadata = json.load(open(metadata_path))

    for work in metadata['works']:
        workid = work['mbid']
        title = work['title']

        try:
            for section in sections_dict[workid]:
                section['title'] = title
        except KeyError:
            pass

    return sections_dict


def generate_score_map(mbid):
    SCORE_PATH = os.path.join(os.path.dirname(__file__), '..', 'scores', mbid)
    fullnames, folders, names = utilities.get_filenames_in_dir(SCORE_PATH,
                                                               '*.svg')
    notes = {}
    for p in fullnames:
        tree, root = svgparser.initialize_svg(p)
        notes_dict = svgparser.get_note_indexes(p, root)
        notes.update(notes_dict)
    return notes


def generate_score_onsets(mbid):
    SCORE_PATH = os.path.join(os.path.dirname(__file__), '..', 'scores', mbid)

    score_indexes = []
    starts = []
    ends = []

    onsets = json.load(open(os.path.join(SCORE_PATH, 'onsets.json')))
    for i in range(len(onsets)-1):
        onset = onsets[i]
        next_note = onsets[i+1][2]

        score_indexes.append(onset[1])
        starts.append(onset[2])
        ends.append(next_note)
    starts.append(onsets[-1][2])
    ends.append(onsets[-1][2])
    score_indexes.append(onsets[-1][1])

    return np.array(starts), np.array(ends), np.array(score_indexes)


def mp3_to_wav_converter(audio_path):
    input_f = audio_path
    output_f = audio_path[:-4] + '.wav'

    os.system('ffmpeg -i {0} {1}'.format(input_f, output_f))


def get_score_sections(metadata):
    sections = {}
    for sec in metadata['sections']:
        duration = [sec['start_note'], sec['end_note']]
        section_name = sec['name'] + '--' + sec['melodic_structure']

        try:
            dur_list = sections[section_name]
            dur_list.append(duration)
            sections[section_name] = dur_list
        except KeyError:
            sections[section_name] = [duration]

    return sections
