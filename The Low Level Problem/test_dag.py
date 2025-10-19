"""
# Ver logs gracias a pytest.ini
pytest -q

# forzando logs por CLI:
pytest -q -o log_cli=true -o log_cli_level=INFO


"""
from typing import List, Tuple
import logging
import pytest

from prog import DAG  

Edge = Tuple[int, int, int]
logger = logging.getLogger("dag_tests")

# ------------------------------
# Logging global para las pruebas
# ------------------------------
@pytest.fixture(autouse=True)
def _configure_logging(caplog):
    # Captura logs a nivel INFO para todas las pruebas
    caplog.set_level(logging.INFO)
    yield


# ------------------------------
# Fixtures con los grafos de prueba
# ------------------------------
@pytest.fixture
def enunciado():
    # Grafo del enunciado (imagen) con Source=0
    edges: List[Edge] = [
        (0, 1, 2),
        (0, 2, 4),
        (0, 4, -2),
        (0, 5, 1),
        (0, 6, 5),
        (2, 3, 3),
        (2, 4, 2),
        (3, 8, -4),
        (4, 3, 5),
        (4, 8, 1),
        (4, 7, 2),
        (5, 7, -1),
        (5, 8, -3),
        (6, 7, 6),
        (7, 8, 2),
    ]
    src = 0
    return edges, src

@pytest.fixture
def caso_fail_3b():
    # Caso donde 3.b es imposible (V = 4 con vecinos {0,1,2,3})
    edges: List[Edge] = [
        (0, 1, 1), (0, 2, 1), (0, 3, 1),
        (1, 4, 1), (2, 4, 1), (3, 4, 1), (0, 4, 1),
    ]
    src = 0
    return edges, src


# ------------------------------
# Tests 
# ------------------------------
def test_path_counts_enunciado(enunciado):
    edges, src = enunciado
    logger.info("Construyendo DAG (enunciado) con %d aristas, source=%d: %s", len(edges), src, edges)
    g = DAG(edges, src)

    cnt = g.path_counts()
    logger.info("Conteo de caminos desde %d: %s", src, cnt)

    expected = {0: 1, 1: 1, 2: 1, 3: 3, 4: 2, 5: 1, 6: 1, 7: 4, 8: 10}
    assert cnt == expected

    most_v = max(cnt, key=lambda v: cnt[v])
    logger.info("Vértice más alcanzable: V=%d con %d caminos", most_v, cnt[most_v])
    assert most_v == 8
    assert cnt[most_v] == 10


def test_enumerate_and_sort_paths_to_V_enunciado(enunciado):
    edges, src = enunciado
    g = DAG(edges, src)
    cnt = g.path_counts()
    target = max(cnt, key=lambda v: cnt[v])

    paths = g.enumerate_paths(target)
    paths_sorted = sorted(paths, key=lambda x: x[1], reverse=True)
    logger.info("Enumerados %d caminos a %d. Ordenados (desc) por costo:\n%s",
                len(paths), target, "\n".join(f"{p[0]} | costo={p[1]}" for p in paths_sorted))

    expected = [
        ([0, 6, 7, 8], 13),
        ([0, 2, 4, 7, 8], 10),
        ([0, 2, 4, 3, 8], 7),
        ([0, 2, 4, 8], 7),
        ([0, 2, 3, 8], 3),
        ([0, 4, 7, 8], 2),
        ([0, 5, 7, 8], 2),
        ([0, 4, 3, 8], -1),
        ([0, 4, 8], -1),
        ([0, 5, 8], -2),
    ]
    assert paths_sorted == expected


def test_neighbors_of_V_enunciado(enunciado):
    edges, src = enunciado
    g = DAG(edges, src)
    neighbors_8 = g.neighbors_of(8)
    logger.info("Vecinos de V=8: %s", neighbors_8)
    assert neighbors_8 == {3, 4, 5, 7}


def test_vprime_insertion_success_enunciado(enunciado):
    edges, src = enunciado
    g = DAG(edges, src)
    cnt = g.path_counts()
    V = max(cnt, key=lambda v: cnt[v])  # debería ser 8
    logger.info("Intentando inserción de V' sobre V=%d (caminos=%d)", V, cnt[V])

    ok, new_edges, msg = g.propose_vprime_insertion(V, weight_default=0)
    logger.info("Resultado inserción V': ok=%s, edges=%s, msg=%s", ok, new_edges, msg)

    assert ok, f"Se esperaba éxito en 3.a/3.b para el enunciado. Mensaje: {msg}"
    assert len(new_edges) == 2

    vprimes = {v for (_, v, _) in new_edges}
    assert len(vprimes) == 1
    vprime = next(iter(vprimes))
    assert vprime == max(g.vertices) + 1

    parents = {u for (u, _, _) in new_edges}
    assert 8 in parents
    extra = list(parents - {8})
    assert len(extra) == 1
    assert extra[0] in {0, 1, 2, 6}


def test_vprime_insertion_impossible(caso_fail_3b):
    edges, src = caso_fail_3b
    g = DAG(edges, src)
    cnt = g.path_counts()
    V = max(cnt, key=lambda v: cnt[v])  # V = 4 con 4 caminos
    logger.info("Intentando inserción de V' sobre V=%d (caminos=%d) en caso imposible", V, cnt[V])

    ok, new_edges, msg = g.propose_vprime_insertion(V, weight_default=0)
    if ok:
        logger.error("Se esperaba fallo por 3.b, pero ok=True. edges=%s, msg=%s", new_edges, msg)
    else:
        logger.warning("Inserción V' IMPOSIBLE como se esperaba: %s", msg)

    assert not ok
    assert new_edges == []
    assert "Imposible satisfacer 3.b" in msg


def test_cycle_detection_raises():
    edges = [(0, 1, 1), (1, 0, 1)]  # ciclo 0<->1
    logger.info("Probando validación de DAG con ciclo: %s", edges)
    with pytest.raises(ValueError):
        DAG(edges, 0)

