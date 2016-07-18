import mne
from mne.datasets import sample
from mne.preprocessing import create_ecg_epochs, create_eog_epochs

# getting some data ready
data_path = 'C:/Anaconda2/Lib/site-packages/examples/mne-testing-data-master'
raw_fname = data_path + '/MEG/sample/sample_audvis_trunc_raw.fif'

raw = mne.io.read_raw_fif(raw_fname, preload=True)


#Show line values
(raw.copy().pick_types(meg='mag')
           .del_proj(0)
           .plot(duration=60, n_channels=100, remove_dc=False))


#Show frequency peaks across measurement media
raw.plot_psd(fmax=250)

#Show data about ECG epochs
average_ecg = create_ecg_epochs(raw).average()
print('We found %i ECG events' % average_ecg.nave)
average_ecg.plot_joint()

