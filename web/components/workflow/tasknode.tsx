import React from "react";
import styles from "./tasknode.module.scss";
import { type NodeProps, type Node, Position, Handle } from "@xyflow/react";

type TaskNodeItem = Node<
  {
    label: string;
    task: string;
  },
  "task"
>;

const TaskNode: React.FC<NodeProps<TaskNodeItem>> = (
  props: NodeProps<TaskNodeItem>
) => {
  return (
    <div className={styles.container}>
      <div>{props.data.label}</div>
      <div>{props.data.task}</div>
      <Handle type="source" position={Position.Right} />
      <Handle type="target" position={Position.Left} />
    </div>
  );
};

export default TaskNode;
