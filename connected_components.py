'''Find connected components of graph given vertices and adjacency lists.'''

from typing import TypeVar

T = TypeVar('T')  # type of vertices in graph


def connected_components(
        vertices: list[T],
        adjacency_lists: dict[T, list[T]]
    ) -> list[list[T]]:
    '''Find connected components of graph given vertices and adjacency lists.'''

    def traverse(v: T) -> None:
        '''Recursive depth first search of component to assign component id.'''

        component_ids[v] = component_id
        for u in adjacency_lists[v]:
            if u not in component_ids:
                traverse(u)

    # Traverse each component to assign component ids
    component_ids: dict[T, int] = {}
    component_id = 0
    for v in vertices:
        if v not in component_ids:
            traverse(v)
            component_id += 1

    # Construct components (in stable order with respect to order in V)
    components: list[list[T]] = [[] for _ in range(component_id)]
    for v in vertices:
        components[component_ids[v]].append(v)
    return components
