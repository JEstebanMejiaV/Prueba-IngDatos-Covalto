
from typing import List, Tuple, Dict, Set
from collections import defaultdict, deque
import argparse

Edge = Tuple[int, int, int]

class DAG:
    """
    DAG con utilidades para:
      (1) contar caminos desde una fuente,
      (2) enumerar caminos y costos hasta un destino,
      (3) proponer inserción de V' cumpliendo 3.a y 3.b.
    """
    def __init__(self, edges: List[Edge], source: int):
        self.edges = edges
        self.src = source
        self.adj = defaultdict(list)      # u -> list[(v, w)]
        self.rev_adj = defaultdict(list)  # v -> list[(u, w)]
        self.vertices: Set[int] = set()
        for u, v, w in edges:
            self.adj[u].append((v, w))
            self.rev_adj[v].append((u, w))
            self.vertices.add(u); self.vertices.add(v)
        if source not in self.vertices:
            self.vertices.add(source)
        self._validate_dag()

    def _validate_dag(self):
        indeg = defaultdict(int)
        for v in self.vertices:
            indeg[v] = 0
        for u, v, _ in self.edges:
            indeg[v] += 1
        q = deque([v for v in self.vertices if indeg[v] == 0])
        topo = []
        while q:
            u = q.popleft()
            topo.append(u)
            for v, _ in self.adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        if len(topo) != len(self.vertices):
            raise ValueError("El grafo no es acíclico (no es DAG)")
        self.topo = topo

    # ---------- Problema 1 ----------
    def path_counts(self) -> Dict[int, int]:
        """Número de caminos distintos desde src a cada vértice (DP topológica)."""
        cnt = {v: 0 for v in self.vertices}
        cnt[self.src] = 1
        for u in self.topo:
            for v, _ in self.adj[u]:
                cnt[v] += cnt[u]
        return cnt

    # ---------- Problema 2 ----------
    def enumerate_paths(self, target: int):
        """Lista de (secuencia_de_nodos, costo) para todos los caminos src->target."""
        # %%
        res = []
        path = [self.src]
        def dfs(u: int, cost: int):
            if u == target:
                res.append((path.copy(), cost))
                return
            for v, w in self.adj[u]:
                path.append(v)
                dfs(v, cost + w)
                path.pop()
        dfs(self.src, 0)
        # %%
        return res

    def neighbors_of(self, v: int) -> Set[int]:
        """Vértices que comparten arista con v (entrantes o salientes). No incluye a v."""
        S = set(u for u, _ in self.rev_adj[v])
        S.update(vv for vv, _ in self.adj[v])
        if v in S:
            S.remove(v)
        return S

    # ---------- Problema 3 ----------
    def propose_vprime_insertion(self, v: int, weight_default: int = 0):
        """
        Propone nuevas aristas (u -> V') con peso por defecto para que:
          a) V' sea el más alcanzable (más caminos desde 0 que V),
          b) Ningún vecino de V comparta arista con V' (3.b).
        Devuelve (ok, new_edges, mensaje).
        """
        # %%
        cnt = self.path_counts()
        max_paths = cnt.get(v, 0)
        banned = self.neighbors_of(v)     # vecinos de V prohibidos
        # candidatos: todos los vértices que NO son vecinos; V mismo está permitido
        candidates = [(u, cnt.get(u, 0)) for u in self.vertices if u not in banned]
        candidates.sort(key=lambda x: x[1], reverse=True)  # mayor cobertura primero

        total = 0
        chosen = []
        for u, c in candidates:
            if c <= 0:
                continue
            chosen.append(u)
            total += c
            if total > max_paths:
                break

        if total <= max_paths:
            reason = (
                "Imposible satisfacer 3.b: aun conectando V' a todos los vértices permitidos "
                f"(excluyendo vecinos de {v}), el número total de caminos ({total}) no supera "
                f"al máximo actual hacia {v} ({max_paths})."
            )
            return (False, [], reason)

        vprime = max(self.vertices) + 1
        new_edges = [(u, vprime, weight_default) for u in chosen]
        # %%
        return (True, new_edges, f"V' = {vprime}; padres elegidos: {chosen}; total caminos = {total} (> {max_paths}).")


# ---------- CLI + función primada para testeo interactivo ----------

def _parse_edge_line(line: str):
    """Extrae una tupla (u,v,w) desde una línea tipo '{u, v, w}' o 'u v w'."""
    import re
    nums = re.findall(r'-?\d+', line)
    if len(nums) != 3:
        raise ValueError(f"No se pudo parsear la arista: {line!r}")
    return tuple(map(int, nums))

def leer_grafo_desde_stdin():
    """
    Lee aristas desde stdin: una por línea, en formato '{u, v, w}' o 'u v w'.
    Línea en blanco para terminar. Luego pide 'source:'.
    """
    # %%
    print("Introduce aristas (una por línea). Ejemplos: {0, 1, 2}  o  0 1 2")
    print("Deja una línea en blanco para finalizar.")
    edges = []
    while True:
        try:
            line = input().strip()
        except EOFError:
            break
        if not line:
            break
        edges.append(_parse_edge_line(line))
    src = int(input("Source vertex: ").strip())
    # %%
    return edges, src


def solve_and_print(edges: List[Edge], source: int):
    """Resuelve e imprime los puntos (1)-(5) para el grafo dado."""
    # %%
    g = DAG(edges, source)
    cnt = g.path_counts()
    most_v = max(cnt.keys(), key=lambda x: cnt[x])
    print(f"(1) Vértice más alcanzable desde {source}: {most_v} con {cnt[most_v]} caminos.")

    paths = g.enumerate_paths(most_v)
    paths_sorted = sorted(paths, key=lambda x: x[1], reverse=True)
    print(f"\n(2) Caminos a {most_v} ordenados por costo descendente:")
    for nodes, cost in paths_sorted:
        print("   ", "->".join(map(str, nodes)), " | costo =", cost)

    ok, new_edges, msg = g.propose_vprime_insertion(most_v, weight_default=0)
    if not ok:
        print("\n(3.b) ERROR:", msg)
        return
    print("\n(3) Inserción V' que satisface 3.a y 3.b:")
    print("   ", msg)
    print("(5) Nuevas aristas (formato {u, v, w}):")
    for u, v, w in new_edges:
        print("   ", f"{{{u}, {v}, {w}}}")
    # %%

def _funcion_primada():

    try:
        edges, src = leer_grafo_desde_stdin()
        solve_and_print(edges, src)
    except Exception as e:
        print("Error:", e)

# ---------- Caso de prueba integrado ----------
def _caso_prueba_basico():

# %%

    # edges_demo: List[Edge] = [
    #     (0, 1, 2), (0, 2, 1),
    #     (1, 3, 5), (2, 3, 1),
    #     (1, 4, 2), (2, 4, 3), (4, 3, 1),
    # ]

    
    # edges_demo: List[Edge] = [
    #     (0, 1, 2),
    #     (0, 2, 4),
    #     (0, 4, -2),
    #     (0, 5, 1),
    #     (0, 6, 5),
    #     (2, 3, 3),
    #     (2, 4, 2),
    #     (3, 8, -4),
    #     (4, 3, 5),
    #     (4, 8, 1),
    #     (4, 7, 2),
    #     (5, 7, -1),
    #     (5, 8, -3),
    #     (6, 7, 6),
    #     (7, 8, 2),
    # ]
    
    
    edges_demo: List[Edge] = [
            (0, 1, 1), (0, 2, 1), (0, 3, 1),
            (1, 4, 1), (2, 4, 1), (3, 4, 1), (0, 4, 1),
        ]
    
    
    src_demo = 0
    print("=== Caso de prueba básico ===")
    solve_and_print(edges_demo, src_demo)
    
    
# %%
if __name__ == "__main__":
    # %%
    parser = argparse.ArgumentParser(description="DAG utilities: conteo de caminos, paths y V'.")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Abrir modo interactivo (función primada).")
    parser.add_argument("--demo", action="store_true",
                        help="Ejecutar el caso de prueba integrado.")
    args = parser.parse_args()

    if args.interactive:
        _funcion_primada()
    else:
        # Por defecto corremos el caso de prueba (o si pasan --demo)
        _caso_prueba_basico()
    # %%
