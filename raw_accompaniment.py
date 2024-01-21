import mido
import os

accords = {}
ind = 60
for i in range(60, 200):
    accords[ind] = [i, i + 3, i + 7]
    accords[ind + 1] = [i, i + 4, i + 7]
    ind += 2


accomp_ind = [75, 124, 112, 110, 164, 105, 95, 99, 52, 40, 9, 23, 55, 52, 0, 147, 153, 161, 217, 11, 87, 31, 80, 260, 45, 207, 90, 195, 128, 249, 183, 93, 75, 206, 10, 30, 22, 236, 45, 162, 10, 17, 28, 191, 47, 137, 11, 22, 95, 69, 87, 242, 42, 72, 18, 86, 59]

bg = mido.MidiFile('data/Minecraft Calm.mid')

play_track = bg.tracks[0]
new_track = mido.MidiTrack()

added_indexes = 0
for i in range(2, len(play_track) - 1):
    ind = i % len(accomp_ind) + 60
    if play_track[i].type == "note_on":
        new_track.insert(i + 1 + added_indexes, mido.Message('note_on', channel=0, note=accords[ind][0], velocity=50, time=100))
        new_track.insert(i + 2 + added_indexes, mido.Message('note_on', channel=0, note=accords[ind][1], velocity=50, time=0))
        new_track.insert(i + 3 + added_indexes, mido.Message('note_on', channel=0, note=accords[ind][2], velocity=50, time=0))

        new_track.insert(i + 4 + added_indexes, mido.Message('note_off', channel=0, note=accords[ind][0], velocity=50, time=100))
        new_track.insert(i + 5 + added_indexes, mido.Message('note_off', channel=0, note=accords[ind][1], velocity=50, time=0))
        new_track.insert(i + 6 + added_indexes, mido.Message('note_off', channel=0, note=accords[ind][2], velocity=50, time=0))

        added_indexes += 6


new_mido = mido.MidiFile()
new_mido.tracks.append(new_track)

track_index = 0
while os.path.exists(f'data/raw_accompaniment_{track_index}.mid'):
    track_index += 1

new_mido.save(f'data/raw_accompaniment_{track_index}.mid')
print(f'FIle saves with name raw_accompaniment_{track_index}.mid')
