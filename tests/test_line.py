import numpy as np

import xline
from xline import elements


def test_line():
    rfmultipole = elements.RFMultipole(
        frequency=100, knl=[0.1, 0.2], ksl=[0.3, 0.4]
    )
    zero_drift = elements.Drift(0)
    line = xline.Line(
        elements=[zero_drift, rfmultipole, zero_drift],
        element_names=["zero_drift", "rfmultipole", "zero_drift"],
    )
    length = 1.4
    drift_exact = elements.DriftExact(length)
    multipole = elements.Multipole(knl=[0.1])
    aperture = elements.LimitEllipse(a=0.08, b=0.02)

    n_elements = 3
    position = 1
    drift_exact_name = "exact drift"
    line.insert_element(position, drift_exact, drift_exact_name)
    n_elements += 1
    assert len(line) == n_elements
    assert line.find_element_ids(drift_exact_name)[0] == position
    assert line.get_length() == length

    multipole_name = "multipole"
    line.insert_element(position, multipole, multipole_name)
    n_elements += 1
    line.insert_element(position + 1, aperture, "multipole_aperture")
    n_elements += 1
    assert len(line) == n_elements

    line._add_offset_error_to(multipole_name, dx=0, dy=0)
    n_elements += 2
    assert len(line) == n_elements

    line._add_offset_error_to(multipole_name, dx=0.2, dy=-0.003)
    n_elements += 2
    assert len(line) == n_elements

    line._add_tilt_error_to(multipole_name, angle=0)
    n_elements += 2
    assert len(line) == n_elements

    line._add_tilt_error_to(multipole_name, angle=0.1)
    n_elements += 2
    assert len(line) == n_elements

    line._add_multipole_error_to(multipole_name, knl=[0, 0.1], ksl=[-0.03, 0.01])
    # line._add_multipole_error_to(drift_exact,knl=[0,0.1],ksl=[-0.03,0.01])

    line_dict = line.to_dict()
    line = xline.Line.from_dict(line_dict)
    assert len(line) == n_elements

    line.append_line(xline.Line.from_dict(line_dict))
    n_elements *= 2
    assert len(line) == n_elements
    assert line.get_length() == 2 * length

    s_elements_d = line.get_s_elements("downstream")
    s_elements_u = line.get_s_elements("upstream")
    assert max(np.array(s_elements_d) - np.array(s_elements_u)) == length

    line.insert_element(1, elements.Multipole(), "inactive_multipole")
    n_elements += 1
    assert len(line) == n_elements
    assert len(line.remove_inactive_multipoles()) == n_elements - 1
    assert len(line) == n_elements
    line.remove_inactive_multipoles(inplace=True)
    n_elements -= 1
    assert len(line) == n_elements

    assert len(line.merge_consecutive_drifts()) == n_elements - 1
    line.merge_consecutive_drifts(inplace=True)
    n_elements -= 1
    assert len(line) == n_elements

    assert len(line.get_elements_of_type(elements.Drift)) == 2

    drifts = line.get_elements_of_type(elements.Drift)[0]
    n_zerolength_drifts = len([d for d in drifts if d.length == 0])
    assert (
        len(line.remove_zero_length_drifts())
        == n_elements - n_zerolength_drifts
    )
    line.remove_zero_length_drifts(inplace=True)
    n_elements -= n_zerolength_drifts
    assert len(line) == n_elements
