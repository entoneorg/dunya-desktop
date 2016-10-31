import tempfile
import os
import json

import compmusic.dunya.makam
from PyQt4 import QtCore


def sort_dictionary(dictionary, key):
    """sorts the given dictionary according to the keys"""
    return sorted(dictionary, key=lambda k: k[key])

def get_attributes():
    makams = compmusic.dunya.makam.get_makams()
    makams = sort_dictionary(makams, 'name')

    forms = compmusic.dunya.makam.get_forms()
    forms = sort_dictionary(forms, 'name')

    usuls = compmusic.dunya.makam.get_usuls()
    usuls = sort_dictionary(usuls, 'name')

    composers = compmusic.dunya.makam.get_composers()
    composers = sort_dictionary(composers, 'name')

    performers = compmusic.dunya.makam.get_artists()
    performers = sort_dictionary(performers, 'name')

    instruments = compmusic.dunya.makam.get_instruments()
    instruments = sort_dictionary(instruments, 'name')

    return makams, forms, usuls, composers, performers, instruments


class FeatureDownloaderThread(QtCore.QThread):
    TEMP = tempfile.gettempdir()
    feautures_downloaded = QtCore.pyqtSignal(dict, dict)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.recid = ''

    def run(self):
        rec_folder = os.path.join(self.TEMP, self.recid)

        if not os.path.exists(rec_folder):
            os.makedirs(rec_folder)

        compmusic.dunya.makam.download_mp3(self.recid, rec_folder,
                                           slugify=True)
        pitch_data = json.loads(compmusic.dunya.docserver.file_for_document(
            self.recid, 'audioanalysis', subtype='pitch_filtered'))
        pd = json.loads(compmusic.dunya.docserver.file_for_document(
            self.recid, 'audioanalysis', subtype='pitch_distribution'))
        self.feautures_downloaded.emit(pitch_data, pd)
