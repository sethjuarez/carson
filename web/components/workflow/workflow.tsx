import React from "react";
import styles from "./workflow.module.scss";
import { useState, useCallback } from "react";
import {
  ReactFlow,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  type NodeChange,
  type EdgeChange,
  type Edge,
  type Node,
  Background,
  Controls,
  MiniMap,
  Panel,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import TaskNode from "./tasknode";
import TaskEdge from "./taskedge";

const initialNodes: Node[] = [
  {
    id: "n1",
    position: { x: 0, y: 0 },
    data: { label: "Node 1", task: "my prompt" },
    type: "taskNode",
  },
  {
    id: "n2",
    position: { x: 0, y: 100 },
    data: { label: "Node 2", task: "another prompt" },
    type: "taskNode",
  },
];
const initialEdges: Edge[] = [
  {
    id: "n1-n2",
    source: "n1",
    target: "n2",
    type: "taskEdge",
    data: { id: "e1", task: "edge task" },
  },
];

type Props = {
  id?: string;
};

const Workflow: React.FC<Props> = ({ id }: Props) => {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);

  const onNodesChange = useCallback(
    (changes: NodeChange<Node>[]) =>
      setNodes((nodesSnapshot) => applyNodeChanges(changes, nodesSnapshot)),
    []
  );
  const onEdgesChange = useCallback(
    (changes: EdgeChange<Edge>[]) =>
      setEdges((edgesSnapshot) => applyEdgeChanges(changes, edgesSnapshot)),
    []
  );
  const onConnect = useCallback(
    (params: any) =>
      setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot)),
    []
  );

  const addNode = () => {
    const newNode = {
      id: `n${nodes.length + 1}`,
      position: { x: Math.random() * 100, y: Math.random() * 100 },
      data: { label: `Node ${nodes.length + 1}`, task: "new task" },
      type: "taskNode",
    };
    setNodes((nds) => nds.concat(newNode));
  };

  // on delete key press, remove selected nodes and edges
  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Delete" || event.key === "Backspace") {
        // find all selected nodes
        const selectedNodes = nodes.filter((node) => node.selected);
        const selectedEdges = edges.filter((edge) => edge.selected);
        // find all edges connected to selected nodes
        const connectedEdges = edges.filter(
          (edge) =>
            selectedNodes.some((node) => node.id === edge.source) ||
            selectedNodes.some((node) => node.id === edge.target)
        );
        const edgesToRemove = [
          ...new Set([...selectedEdges, ...connectedEdges]),
        ];
        // remove selected nodes and connected edges
        setNodes((nds) => nds.filter((node) => !node.selected));
        setEdges((eds) => eds.filter((edge) => !edgesToRemove.includes(edge)));
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <div className={styles.container}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={{
          taskNode: TaskNode,
        }}
        edgeTypes={{
          taskEdge: TaskEdge,
        }}
        proOptions={{ hideAttribution: true }}
        fitView
      >
        <Panel position="top-left" className={styles.panel}>
          <button onClick={addNode}>Click Me</button>
        </Panel>
        <Background />
        <MiniMap nodeStrokeWidth={3} />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default Workflow;
