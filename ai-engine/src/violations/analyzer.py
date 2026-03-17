from utils.bbox_utils import get_bbox_center, get_bbox_height

class ViolationsAnalyser:
    RIDING_POSES = {'riding', 'climbing'}
    IGNORED_POSES = {'on_foot', 'other'}

    SURFACE_VIOLATIONS = {
        'riding': {
            'road': 'ride_on_the_unacceptable',
            'unacceptable': 'ride_on_the_unacceptable',
            'crosswalk': 'ride_on_the_crosswalk'
        },
        'pushing': {
            'road': 'walk_on_the_unacceptable',
            'unacceptable': 'walk_on_the_unacceptable'
        }
    }

    def analyze(self, predictions, scooters):
        used_scooters = {}

        if predictions:
            for p in predictions:
                self._process_prediction(p, used_scooters)

        if scooters:
            self._process_scooters(scooters, used_scooters)

    def _process_prediction(self, p, used_scooters):
        scooter = p['nearest_scooter']
        if not scooter or p['class'] in self.IGNORED_POSES:
            return

        scooter_id = str(scooter['bbox'][0])
        self._check_two_person_violation(p, scooter_id, used_scooters)
        self._check_surface_violations(p, p['class'], scooter['surface'])

    def _check_two_person_violation(self, p, scooter_id, used_scooters):
        if scooter_id not in used_scooters:
            used_scooters[scooter_id] = p['bbox']
            return

        if self._is_same_person(p['bbox'], used_scooters[scooter_id]):
            p['violations'].append('two_person_violation')

    def _is_same_person(self, bbox1, bbox2):
        h1, h2 = get_bbox_height(bbox1), get_bbox_height(bbox2)
        c1, c2 = get_bbox_center(bbox1), get_bbox_center(bbox2)

        height_diff = abs(h1 / h2)
        center_diff = abs(c1[1] - c2[1]) / h1

        return 0.6 < height_diff < 1.7 and center_diff < 0.2

    def _check_surface_violations(self, p, pose, surface):
        if pose in self.SURFACE_VIOLATIONS and surface in self.SURFACE_VIOLATIONS[pose]:
            p['violations'].append(self.SURFACE_VIOLATIONS[pose][surface])

    def _process_scooters(self, scooters, used_scooters):
        for scooter in scooters:
            scooter_id = str(scooter['bbox'][0])
            if scooter_id not in used_scooters and scooter['surface'] in {'road', 'unacceptable', 'crosswalk'}:
                scooter['warning'] = ['in_the_wrong_place']