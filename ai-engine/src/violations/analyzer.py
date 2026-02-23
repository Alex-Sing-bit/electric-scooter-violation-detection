class ViolationsAnalyser:
    def analyze(self, predictions, scooters):
        used_scooters = []
        if predictions:
            for p in predictions:
                scooter = p['nearest_scooter']
                pose = p['class']
                if scooter is None:
                    continue
                if scooter not in used_scooters and pose in ['riding', 'climbing', 'pushing']:
                    used_scooters.append(scooter)
                else:
                    p['violations'] = ['two_person_violation']

            for p in predictions:
                scooter = p['nearest_scooter']
                surface = scooter['surface'] if scooter is not None else None
                pose = p['class']
                if pose == 'riding' or pose == 'climbing':
                    if surface == 'acceptable':
                        continue
                    elif surface == 'road' or surface == 'unacceptable':
                        p['violations'] = ['ride_on_the_unacceptable']
                    elif surface == 'crosswalk':
                        p['violations'] = ['ride_on_the_crosswalk']
                if pose == 'pushing':
                    if surface == 'acceptable' or surface == 'crosswalk':
                        continue
                    elif surface == 'road' or surface == 'unacceptable':
                        p['violations'] = ['walk_on_the_unacceptable']
        if scooters:
            for scooter in scooters:
                if scooter not in used_scooters:
                    if scooter['surface'] == 'unacceptable':
                        scooter['warning'] = ['in_the_wrong_place']


