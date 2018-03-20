import argparse
from collections import defaultdict, namedtuple
import time
import os

from graphviz import Digraph
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

Edge = namedtuple('Edge', ['src', 'dst', 'done'])
Node = namedtuple('Node', ['name', 'done', 'goal'])

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate mikado graph from description.')

    parser.add_argument('file', type=str, help='Mikado description file')
    parser.add_argument('-o', '--output', type=str, help='Mikado graph output')
    parser.add_argument('-v', '--view', action='store_true', help='View generated Mikado graph')

    return parser.parse_args()

def parse_mikado_description(description_file):
    with open(description_file, 'r') as file:
        text = file.read()
        lines = text.split('\n')

        tasks = list((line.lstrip(), _depth_level(line)) for line in lines if len(line) > 0)

        nodes = list(Node(name=_task_strip(task), done=_task_done(task), goal=depth==0) for task, depth in set(tasks))
        edges = list(Edge(src=_task_strip(src), dst=_task_strip(dst), done=_task_done(src) and _task_done(dst))
                         for src, dst in set(_mikado_pairs(tasks, list(), list())))

        return nodes, edges

def _task_done(task):
    return task.startswith('x')

def _task_strip(task):
    return ' '.join(task.split(' ')[1:]).lstrip()

def _depth_level(line):
    return int(_count_indentation(line) / 4)

def _count_indentation(line, count=0):
    if line.startswith(' '): return _count_indentation(line[1:], count + 1)
    else:                    return count

def _mikado_pairs(tasks, mikado_pairs, parents):
    if len(tasks) == 0: return mikado_pairs

    child, depth = tasks[0]

    if len(parents):
        mikado_pairs.append((parents[-(len(parents) - depth + 1)], child))

    if len(parents) != depth:
        return _mikado_pairs(tasks=tasks[1:], mikado_pairs=mikado_pairs, parents=[*parents[:depth], child])
    else:
        return _mikado_pairs(tasks=tasks[1:], mikado_pairs=mikado_pairs, parents=[*parents, child])

def draw_mikado_graph(nodes, edges):
    graph = Digraph(strict=True)
    for node in nodes: _append_node(graph, node)
    for edge in edges: _append_edge(graph, edge)
    return graph

def _append_node(graph, node):
    color = 'green' if node.done else 'black'
    graph.node(node.name, color=color, fontcolor=color, peripheries='2' if node.goal else '1')

def _append_edge(graph, edge):
    color = 'green' if edge.done else 'black'
    graph.edge(edge.src, edge.dst, color=color)

def render_graph(mikado_description, view, output_file):
    graph = draw_mikado_graph(*parse_mikado_description(mikado_description))
    graph.render(view=view, cleanup=True)

    if output_file:
        graph.save(output_file)

def main():
    args = parse_arguments()

    render_graph(args.file, args.view, args.output)

if __name__ == '__main__':
    main()