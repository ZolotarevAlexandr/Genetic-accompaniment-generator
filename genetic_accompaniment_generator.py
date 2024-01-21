import random
import mido
import os
from tqdm import tqdm


def create_chromosome():
    return [random.randint(60, len(accords) - 1) for _ in range(chromosome_length)]


def proximity_error(gen):
    for note in notes:
        accord = accords[gen]
        for note_gen in accord:
            if abs(note - note_gen) <= 2:
                return 10
    return 0


def fitness(chromosome):
    error = 0

    for gen in chromosome:
        # Penalize accords with notes that are too close to melody
        error += proximity_error(gen)

    for i, gen in enumerate(chromosome):
        # Calculate the error as the sum of differences between melody and accompaniment notes
        note_error = sum(abs(avg_note - accords[gen][j]) for j in range(3))
        error += round(note_error / 5)

        # Penalize consecutive accompaniment notes that are far apart
        if i > 0:
            prev_gen = chromosome[i - 1]
            interval_error = abs(accords[gen][0] - accords[prev_gen][0])
            error += round(interval_error / 10)

    return error


def selection(population):
    selected = random.sample(population, population_size // 40)
    return min(selected, key=lambda chromosome: fitness(chromosome))


def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child = parent1[:crossover_point] + parent2[crossover_point:]
    return child


def mutate(chromosome):
    for i in range(len(chromosome)):
        if random.random() < mutation_rate:
            chromosome[i] = random.randint(60, len(accords) - 1)
    return chromosome


def get_notes(midi_file: mido.MidiFile):
    notes = []
    for msg in midi_file.tracks[0]:
        if msg.is_meta or msg.type != 'note_on':
            continue
        notes.append(msg.note)
    return notes


midi_file = mido.MidiFile('data/Minecraft Calm.mid')

accords = {}
ind = 60
for i in range(60, 121):
    accords[ind] = [i, i + 3, i + 7]
    accords[ind + 1] = [i, i + 4, i + 7]
    ind += 2

notes = list(set(get_notes(midi_file)))
all_notes = get_notes(midi_file)
avg_note = sum(notes) // len(notes)

# Genetic Algorithm parameters
population_size = 500  # Original value: 500
mutation_rate = 0.25   # Original value: 0.5 (My standard value: 0.25)
num_generations = 400  # Original value: 400
chromosome_length = 20

# Generate initial population
population = [create_chromosome() for _ in range(population_size)]

# Evolutionary loop
for generation in tqdm(range(num_generations)):
    # Evaluate fitness of each chromosome
    # print("population", population)
    fitness_scores = [fitness(chromosome) for chromosome in population]

    # Create the next generation
    next_generation = []
    for _ in range(population_size // 2):
        # Selection
        parent1 = selection(population)
        parent2 = selection(population)

        # Crossover
        child1 = crossover(parent1, parent2)
        child2 = crossover(parent2, parent1)

        # Mutation
        child1 = mutate(child1)
        child2 = mutate(child2)

        # Add children to the next generation
        next_generation.extend([child1, child2])

    # Replace the current generation with the next generation
    population = next_generation

# Find the best solution
fitness_scores = [fitness(chromosome) for chromosome in population]
ind = fitness_scores.index(min(fitness_scores))
best_population = population[ind]
best_error = min(fitness_scores)

# Print the best solution
print(f"Best Solution: {best_population}")
print(f'With error: {best_error}')

play_track = midi_file.tracks[0]
new_track = midi_file.tracks[0][:-1]

added_indexes = 0
for i in range(2, len(play_track) - 1):
    ind = i % len(best_population)
    if play_track[i].type == "note_on":
        new_track.insert(i + 1 + added_indexes, mido.Message('note_on', channel=0, note=accords[best_population[ind]][0], velocity=30, time=0))
        new_track.insert(i + 2 + added_indexes, mido.Message('note_on', channel=0, note=accords[best_population[ind]][1], velocity=30, time=0))
        new_track.insert(i + 3 + added_indexes, mido.Message('note_on', channel=0, note=accords[best_population[ind]][2], velocity=30, time=0))

        new_track.insert(i + 4 + added_indexes, mido.Message('note_off', channel=0, note=accords[best_population[ind]][0], velocity=30, time=50))
        new_track.insert(i + 5 + added_indexes, mido.Message('note_off', channel=0, note=accords[best_population[ind]][1], velocity=30, time=0))
        new_track.insert(i + 6 + added_indexes, mido.Message('note_off', channel=0, note=accords[best_population[ind]][2], velocity=30, time=0))

        added_indexes += 6

new_track.append(midi_file.tracks[0][-1])
midi_file.tracks[0] = new_track

track_index = 0
while any(map(lambda x: x.startswith(f'test_track_{track_index}'), os.listdir('data'))):
    track_index += 1

midi_file.save(f"data/test_track_{track_index}_{best_error}_{num_generations}.mid")
print(f'File saved with name "test_track_{track_index}_{best_error}_{num_generations}.mid"')

print('Keep this generation?')
save = input('[Y] - Yes [N] - No: ')
if save == 'N':
    os.remove(f'data/test_track_{track_index}_{best_error}_{num_generations}.mid')
